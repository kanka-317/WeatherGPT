from datetime import datetime, timezone, timedelta
import json
import re
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import openai

from app.core.config import settings
from app.models.chat import ChatMessage
from app.schemas.chat import ChatResponse
from app.services.llm_tools import WEATHER_TOOLS, execute_tool_call
from app.services.weather_service import WeatherService

IST_TZ = timezone(timedelta(hours=5, minutes=30))

def format_timestamp_ist(ts_val) -> str:
    """Formats an ISO string or datetime object into human-readable Indian Standard Time matching local clock."""
    if not ts_val:
        return datetime.now(IST_TZ).strftime("%I:%M %p, %d-%m-%Y")
    
    dt = None
    if isinstance(ts_val, datetime):
        dt = ts_val
    elif isinstance(ts_val, str):
        try:
            clean_str = ts_val.strip()
            if not clean_str.endswith("Z") and "+" not in clean_str and "-" not in clean_str[10:]:
                clean_str += "+00:00"
            else:
                clean_str = clean_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_str)
        except Exception:
            pass

    if dt is None:
        dt = datetime.now(IST_TZ)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    dt_ist = dt.astimezone(IST_TZ)
    return dt_ist.strftime("%I:%M %p, %d-%m-%Y")

SYSTEM_PROMPT = """You are WeatherGPT, an AI meteorological and agro-weather intelligence assistant developed for SIH Problem Statement 26068.
You provide accurate, hyper-local weather reports, forecasts, and actionable advisory for citizens and farmers.

STRICT OPERATIONAL RULES:
1. NEVER invent or hallucinate a weather alert or warning that is not explicitly present in the alerts data. If there are no alerts, clearly state that no warnings are active.
2. ALWAYS cite the data source (e.g. OpenWeather or IMD) and include the observation/forecast timestamp (e.g. "as of <timestamp>") in your answer.
3. If no location is provided in the message, conversation history, or coordinate parameters, DO NOT GUESS OR DEFAULT TO A RANDOM CITY. Ask the user politely to specify their location (city, district, or state).
4. For agricultural and farmer advisories (e.g., "should I irrigate tomorrow?"):
   - Base your advice directly on the forecast precipitation (rainfall in mm), probability of rain, wind speed, and temperature.
   - If rainfall (>1 mm) is expected tomorrow, advise pausing or delaying irrigation to prevent crop damage and save resources.
   - If dry or hot weather is forecast, advise irrigating early morning or late evening.
"""

_OPENAI_QUOTA_EXHAUSTED = False


class LLMService:
    def __init__(self, db: AsyncSession, weather_service: Optional[WeatherService] = None):
        self.db = db
        self.weather_service = weather_service or WeatherService(db=db)
        self.api_key = settings.OPENAI_API_KEY

    async def chat(
        self,
        message: str,
        session_id: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        language: str = "en",
    ) -> ChatResponse:
        """Process incoming chat query through multi-turn LLM + tool calling pipeline with multilingual support."""
        global _OPENAI_QUOTA_EXHAUSTED
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Detect language from input script if not explicitly overridden
        lang = (language or "en").lower()
        if re.search(r'[\u0980-\u09FF]', message):
            lang = "bn"
        elif re.search(r'[\u0900-\u097F]', message):
            lang = "hi"

        # 1. Record user message in DB
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=message,
            created_at=now,
        )
        self.db.add(user_msg)
        await self.db.commit()

        # 2. Retrieve session history for context
        history_stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        history_res = await self.db.execute(history_stmt)
        past_messages = history_res.scalars().all()

        tools_invoked: List[str] = []

        # 3. Check if OpenAI API key is active
        is_real_openai = (
            bool(self.api_key)
            and not self.api_key.startswith("your_")
            and self.api_key != "mock_or_real_openai_key"
            and not _OPENAI_QUOTA_EXHAUSTED
        )

        if is_real_openai:
            try:
                reply = await self._run_openai_pipeline(
                    past_messages=past_messages,
                    session_id=session_id,
                    lat=lat,
                    lon=lon,
                    tools_invoked=tools_invoked,
                    language=lang,
                )
                return ChatResponse(
                    reply=reply,
                    session_id=session_id,
                    language=lang,
                    tools_called=tools_invoked,
                    timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                )
            except Exception as e:
                err_str = str(e).lower()
                if "insufficient_quota" in err_str or "429" in err_str:
                    _OPENAI_QUOTA_EXHAUSTED = True
                print(f"[LLMService] OpenAI error or quota exceeded, switching to deterministic handler: {e}")
                # Fall through to deterministic handler

        # 4. Deterministic handler (resilient fallback for tests, offline development, and demos)
        reply = await self._run_deterministic_pipeline(
            message=message,
            session_id=session_id,
            lat=lat,
            lon=lon,
            tools_invoked=tools_invoked,
            language=lang,
        )

        return ChatResponse(
            reply=reply,
            session_id=session_id,
            language=lang,
            tools_called=tools_invoked,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
        )

    async def _run_openai_pipeline(
        self,
        past_messages: List[ChatMessage],
        session_id: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        tools_invoked: Optional[List[str]] = None,
        language: str = "en",
    ) -> str:
        """Standard OpenAI Tool-Calling Loop using AsyncOpenAI with multilingual instruction."""
        client = openai.AsyncOpenAI(api_key=self.api_key, max_retries=1, timeout=25.0)

        lang_instruction = ""
        if language == "bn":
            lang_instruction = (
                "\n\nCRITICAL MULTILINGUAL RULE: The user has selected Bengali (বাংলা) or submitted a query in Bengali. "
                "You MUST generate your final response entirely in natural, fluent, and helpful Bengali (বাংলা). "
                "Do NOT reply in English."
            )
        elif language == "hi":
            lang_instruction = (
                "\n\nCRITICAL MULTILINGUAL RULE: The user has selected Hindi (हिन्दी) or submitted a query in Hindi. "
                "You MUST generate your final response entirely in natural, fluent, and helpful Hindi (हिन्दी). "
                "Do NOT reply in English."
            )

        openai_messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT + lang_instruction}
        ]

        # Populate context from history
        for msg in past_messages:
            msg_dict: Dict[str, Any] = {"role": msg.role, "content": msg.content or ""}
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            openai_messages.append(msg_dict)

        # First call to OpenAI
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            tools=WEATHER_TOOLS,
            tool_choice="auto",
            temperature=0.2,
        )

        assistant_msg = response.choices[0].message

        # Handle tool calls if requested
        while assistant_msg.tool_calls:
            serialized_tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_msg.tool_calls
            ]

            # Save assistant tool request turn
            db_turn = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=assistant_msg.content,
                tool_calls=serialized_tool_calls,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            self.db.add(db_turn)
            await self.db.commit()

            openai_messages.append({
                "role": "assistant",
                "content": assistant_msg.content,
                "tool_calls": serialized_tool_calls,
            })

            # Execute tool calls
            for tc in assistant_msg.tool_calls:
                func_name = tc.function.name
                if tools_invoked is not None:
                    tools_invoked.append(func_name)
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}

                tool_output = await execute_tool_call(
                    name=func_name,
                    arguments=args,
                    weather_service=self.weather_service,
                    default_lat=lat,
                    default_lon=lon,
                )

                tool_content_str = json.dumps(tool_output, default=str)

                # Save tool response turn in DB
                db_tool = ChatMessage(
                    session_id=session_id,
                    role="tool",
                    content=tool_content_str,
                    tool_call_id=tc.id,
                    created_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )
                self.db.add(db_tool)
                await self.db.commit()

                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": func_name,
                    "content": tool_content_str,
                })

            # Follow-up completion after tools
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=openai_messages,
                tools=WEATHER_TOOLS,
                temperature=0.2,
            )
            assistant_msg = response.choices[0].message

        final_reply = assistant_msg.content or "I have processed your weather request."

        # Save final assistant reply
        db_final = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=final_reply,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        self.db.add(db_final)
        await self.db.commit()

        return final_reply

    async def _run_deterministic_pipeline(
        self,
        message: str,
        session_id: str,
        lat: Optional[float],
        lon: Optional[float],
        tools_invoked: List[str],
        language: str = "en",
    ) -> str:
        """Deterministic NLP extractor and tool executor for offline/demo/testing resilience with multilingual support."""
        msg_lower = message.lower()

        # Multilingual place mappings
        place_mappings = {
            "kolkata": "Kolkata", "কলকাতা": "Kolkata", "कोलकाता": "Kolkata",
            "nadia": "Nadia", "নদীয়া": "Nadia", "নদিয়া": "Nadia", "नादिया": "Nadia",
            "darjeeling": "Darjeeling", "দার্জিলিং": "Darjeeling", "दार्जिलिंग": "Darjeeling",
            "south 24 parganas": "South 24 Parganas", "s 24 parganas": "South 24 Parganas",
            "দক্ষিণ ২৪ পরগনা": "South 24 Parganas", "दक्षिण 24 परगना": "South 24 Parganas",
            "sunderbans": "South 24 Parganas", "sundarbans": "South 24 Parganas", "সুন্দরবন": "South 24 Parganas",
            "howrah": "Howrah", "হাওড়া": "Howrah", "हावड़ा": "Howrah",
            "delhi": "Delhi", "দিল্লি": "Delhi", "दिल्ली": "Delhi",
            "mumbai": "Mumbai", "মুম্বাই": "Mumbai", "मुंबई": "Mumbai",
            "chennai": "Chennai", "bengaluru": "Bengaluru", "hyderabad": "Hyderabad", "pune": "Pune",
        }

        detected_location = None
        for key, val in place_mappings.items():
            if key in message or key in msg_lower:
                detected_location = val
                break

        # If no location in text, check coordinate args
        has_coords = (lat is not None and lon is not None)

        # Check for clarifying question trigger: No location given or inferable
        if not detected_location and not has_coords:
            match = re.search(r'\bin\s+([a-zA-Z]+)', message, re.IGNORECASE)
            if match:
                detected_location = match.group(1).capitalize()
            else:
                if language == "bn":
                    clarifying_reply = (
                        "আপনি কোন শহর বা জেলার আবহাওয়া জানতে চান? "
                        "অনুগ্রহ করে আপনার অবস্থান (যেমন কলকাতা, নদীয়া, দার্জিলিং) উল্লেখ করুন।"
                    )
                elif language == "hi":
                    clarifying_reply = (
                        "आप किस शहर या जिले का मौसम जानना चाहते हैं? "
                        "कृपया अपना स्थान (जैसे कोलकाता, नादिया, दार्जिलिंग) बताएं ताकि मैं सही जानकारी दे सकूँ।"
                    )
                else:
                    clarifying_reply = (
                        "Which city, district, or coordinates are you inquiring about? "
                        "Please provide a location so I can fetch accurate weather data."
                    )
                db_reply = ChatMessage(
                    session_id=session_id,
                    role="assistant",
                    content=clarifying_reply,
                    created_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )
                self.db.add(db_reply)
                await self.db.commit()
                return clarifying_reply

        # Differentiate specific query intents
        temp_keywords = ["temp", "temperature", "hot", "cold", "heat", "degree", "তাপমাত্রা", "গরম", "ঠান্ডা", "तापमान", "गर्मी", "ठंड"]
        wind_keywords = ["wind", "breeze", "squall", "gust", "বাতাস", "ঝড়", "হওয়া", "হাওয়া", "हवा", "आंधी"]
        humidity_keywords = ["humidity", "humid", "moisture", "আর্দ্রতা", "नमी"]
        alert_keywords = ["alert", "warning", "cyclone", "flood", "disaster", "danger", "সতর্কতা", "সাইক্লোন", "বন্যা", "দুর্যোগ", "বিপদ", "चेतावनी", "चक्रवात", "बाढ़", "खतरा"]
        forecast_keywords = [
            "tomorrow", "forecast", "next", "days", "weekend", "rain tomorrow",
            "কাল", "কালকে", "আগামীকাল", "পরশু",
            "कल", "आने वाले", "परसों"
        ]

        is_temp_query = any(w in message or w in msg_lower for w in temp_keywords)
        is_wind_query = any(w in message or w in msg_lower for w in wind_keywords)
        is_humidity_query = any(w in message or w in msg_lower for w in humidity_keywords)
        is_alert_query = any(w in message or w in msg_lower for w in alert_keywords)
        is_forecast = any(w in message or w in msg_lower for w in forecast_keywords) and not (is_temp_query and "now" in msg_lower)

        advisory_keywords = [
            "irrigate", "irrigation", "water my crops", "watering",
            "সেচ", "পানি দেব", "পানি দেওয়া",
            "सिंचाई", "पानी देना"
        ]
        is_irrigation_advisory = any(w in message or w in msg_lower for w in advisory_keywords)

        if is_forecast:
            # Call get_forecast tool
            tools_invoked.append("get_forecast")
            forecast_data = await execute_tool_call(
                name="get_forecast",
                arguments={"location_name": detected_location, "lat": lat, "lon": lon, "days": 3},
                weather_service=self.weather_service,
                default_lat=lat,
                default_lon=lon,
            )

            # Also check for active alerts
            tools_invoked.append("get_active_alerts")
            alerts_data = await execute_tool_call(
                name="get_active_alerts",
                arguments={"location_name": detected_location, "lat": lat, "lon": lon},
                weather_service=self.weather_service,
                default_lat=lat,
                default_lon=lon,
            )

            # Store tool execution turns in DB
            db_tool_forecast = ChatMessage(
                session_id=session_id,
                role="tool",
                content=json.dumps(forecast_data, default=str),
                tool_call_id="call_forecast_001",
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            self.db.add(db_tool_forecast)

            forecast_list = forecast_data.get("forecast", [])
            loc_name = detected_location or forecast_data.get("location", {}).get("name", "Kolkata")
            if loc_name.startswith("Coord (") and detected_location:
                loc_name = detected_location

            tomorrow_slot = forecast_list[1] if len(forecast_list) > 1 else (forecast_list[0] if forecast_list else {})
            rainfall = tomorrow_slot.get("rainfall", 0.0)
            condition = tomorrow_slot.get("condition", "Partly Cloudy")
            temp = tomorrow_slot.get("temperature", 30.0)
            timestamp_str = format_timestamp_ist(tomorrow_slot.get("timestamp"))

            alerts = alerts_data.get("alerts", [])

            if language == "bn":
                loc_bn = {"Kolkata": "কলকাতা", "Nadia": "নদীয়া", "Darjeeling": "দার্জিলিং", "South 24 Parganas": "দক্ষিণ ২৪ পরগনা", "Delhi": "দিল্লি", "Mumbai": "মুম্বাই"}.get(loc_name, loc_name)
                alerts_text_bn = f" সতর্কতা: {alerts[0]['type']} - '{alerts[0]['message']}'" if alerts else " বর্তমানে কোনো মারাত্মক দুর্যোগের সতর্কতা নেই।"

                if is_irrigation_advisory:
                    if rainfall > 1.0 or "rain" in condition.lower():
                        final_reply = (
                            f"**{loc_bn}-এর কৃষকদের জন্য পরামর্শ**: কাল **সেচ দেওয়া স্থগিত রাখা উচিত**। "
                            f"পূর্বাভাস অনুযায়ী (OpenWeather-এর তথ্য অনুযায়ী, সময়: {timestamp_str}), কাল প্রায় {rainfall:.1f} মিমি বৃষ্টিপাতের সম্ভাবনা রয়েছে "
                            f"এবং তাপমাত্রা প্রায় {temp}°C থাকবে।{alerts_text_bn} "
                            f"সেচ না দিলে ফসলের ক্ষতি ও অতিরিক্ত জলাবদ্ধতা এড়ানো যাবে।"
                        )
                    else:
                        final_reply = (
                            f"**{loc_bn}-এর কৃষকদের জন্য পরামর্শ**: কাল সেচ দেওয়ার উপযোগী অনুকূল আবহাওয়া থাকবে। "
                            f"পূর্বাভাস অনুযায়ী (OpenWeather-এর তথ্য অনুযায়ী, সময়: {timestamp_str}), উল্লেখযোগ্য কোনো বৃষ্টির সম্ভাবনা নেই ({rainfall:.1f} মিমি) "
                            f"এবং তাপমাত্রা প্রায় {temp}°C থাকবে।{alerts_text_bn} "
                            f"ভোরের দিকে বা বিকেলে সেচ দেওয়ার পরামর্শ দেওয়া হচ্ছে।"
                        )
                else:
                    if rainfall > 0.0 or "rain" in condition.lower():
                        final_reply = (
                            f"পূর্বাভাস অনুযায়ী (OpenWeather-এর তথ্য অনুযায়ী, সময়: {timestamp_str}), "
                            f"**হ্যাঁ, কাল {loc_bn}-এ বৃষ্টি হওয়ার সম্ভাবনা রয়েছে**। "
                            f"প্রায় {rainfall:.1f} মিমি বৃষ্টিপাতের পূর্বাভাস রয়েছে, আকাশ {condition.lower()} থাকবে এবং গড় তাপমাত্রা প্রায় {temp}°C হতে পারে।{alerts_text_bn}"
                        )
                    else:
                        final_reply = (
                            f"পূর্বাভাস অনুযায়ী (OpenWeather-এর তথ্য অনুযায়ী, সময়: {timestamp_str}), "
                            f"**কাল {loc_bn}-এ বৃষ্টির সম্ভাবনা কম**। "
                            f"আকাশ মূলত পরিষ্কার বা আংশিক মেঘলা থাকবে, গড় তাপমাত্রা প্রায় {temp}°C এবং বৃষ্টিপাতের সম্ভাবনা মাত্র {rainfall:.1f} মিমি।{alerts_text_bn}"
                        )

            elif language == "hi":
                loc_hi = {"Kolkata": "कोलकाता", "Nadia": "नादिया", "Darjeeling": "दार्जिलिंग", "South 24 Parganas": "दक्षिण 24 परगना", "Delhi": "दिल्ली", "Mumbai": "मुंबई"}.get(loc_name, loc_name)
                alerts_text_hi = f" चेतावनी: {alerts[0]['type']} - '{alerts[0]['message']}'" if alerts else " वर्तमान में कोई गंभीर चेतावनी नहीं है।"

                if is_irrigation_advisory:
                    if rainfall > 1.0 or "rain" in condition.lower():
                        final_reply = (
                            f"**{loc_hi} के किसानों के लिए सलाह**: कल **सिंचाई रोक देना बेहतर होगा**। "
                            f"मौसम पूर्वानुमान (समय: {timestamp_str}, OpenWeather) के अनुसार कल {rainfall:.1f} मिमी बारिश की संभावना है "
                            f"और तापमान लगभग {temp}°C रहेगा।{alerts_text_hi} इससे जलभराव और फसलों को नुकसान से बचाया जा सकेगा।"
                        )
                    else:
                        final_reply = (
                            f"**{loc_hi} के किसानों के लिए सलाह**: कल सिंचाई के लिए मौसम अनुकूल है। "
                            f"मौसम पूर्वानुमान (समय: {timestamp_str}, OpenWeather) के अनुसार शुष्क मौसम और लगभग {rainfall:.1f} मिमी वर्षा की संभावना है।{alerts_text_hi} "
                            f"सुबह या शाम के समय सिंचाई करने की सलाह दी जाती है।"
                        )
                else:
                    if rainfall > 0.0 or "rain" in condition.lower():
                        final_reply = (
                            f"मौसम पूर्वानुमान के अनुसार (OpenWeather डेटा, समय: {timestamp_str}), "
                            f"**हाँ, कल {loc_hi} में बारिश होने की संभावना है**। "
                            f"लगभग {rainfall:.1f} मिमी वर्षा का अनुमान है और औसत तापमान {temp}°C रहेगा।{alerts_text_hi}"
                        )
                    else:
                        final_reply = (
                            f"मौसम पूर्वानुमान के अनुसार (OpenWeather डेटा, समय: {timestamp_str}), "
                            f"**कल {loc_hi} में बारिश की संभावना नहीं है**। "
                            f"मौसम सामान्य रहेगा, तापमान लगभग {temp}°C और वर्षा मात्र {rainfall:.1f} मिमी रहने का अनुमान है।{alerts_text_hi}"
                        )

            else:
                # English forecast response
                alerts_text = ""
                if alerts:
                    alerts_text = f" Active Alert: {alerts[0]['type']} - '{alerts[0]['message']}' (Source: {alerts[0]['source']})."
                else:
                    alerts_text = " There are currently no active severe weather warnings for this area."

                if is_irrigation_advisory:
                    if rainfall > 1.0 or "rain" in condition.lower():
                        final_reply = (
                            f"**Advisory for {loc_name}**: You should **hold off on irrigating tomorrow**. "
                            f"Forecast data (as of {timestamp_str}, via OpenWeather) indicates expected rainfall of {rainfall:.1f} mm "
                            f"with {condition.lower()} conditions and a temperature of around {temp}°C.{alerts_text} "
                            f"Delaying irrigation will prevent waterlogging and conserve water resources."
                        )
                    else:
                        final_reply = (
                            f"**Advisory for {loc_name}**: Conditions are favorable for irrigation. "
                            f"Forecast data (as of {timestamp_str}, via OpenWeather) shows dry conditions ({condition}) with no significant rain ({rainfall:.1f} mm) "
                            f"and temperatures around {temp}°C.{alerts_text} "
                            f"We recommend irrigating in the early morning or evening to minimize evaporative loss."
                        )
                else:
                    if rainfall > 0.0 or "rain" in condition.lower():
                        final_reply = (
                            f"According to forecast data (as of {timestamp_str}, via OpenWeather), "
                            f"**yes, rain is expected in {loc_name} tomorrow**. The forecast predicts {rainfall:.1f} mm of precipitation "
                            f"with {condition.lower()} skies and an average temperature of {temp}°C.{alerts_text}"
                        )
                    else:
                        final_reply = (
                            f"According to forecast data (as of {timestamp_str}, via OpenWeather), "
                            f"**rain is unlikely in {loc_name} tomorrow**. Expect {condition.lower()} conditions with "
                            f"temperatures reaching around {temp}°C and {rainfall:.1f} mm precipitation.{alerts_text}"
                        )

        else:
            # Current weather & observation flow
            tools_invoked.append("get_current_weather")
            current_data = await execute_tool_call(
                name="get_current_weather",
                arguments={"location_name": detected_location, "lat": lat, "lon": lon},
                weather_service=self.weather_service,
                default_lat=lat,
                default_lon=lon,
            )

            # Store tool turn
            db_tool_current = ChatMessage(
                session_id=session_id,
                role="tool",
                content=json.dumps(current_data, default=str),
                tool_call_id="call_current_001",
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            self.db.add(db_tool_current)

            obs = current_data.get("observation", {})
            loc_name = current_data.get("location", {}).get("name", detected_location or "your location")
            source = obs.get("source", "OpenWeather")
            temp = obs.get("temperature", "--")
            humidity = obs.get("humidity", "--")
            cond = obs.get("condition", "Clear")
            wind = obs.get("wind_speed", "--")
            timestamp_str = format_timestamp_ist(obs.get("timestamp"))

            alerts = current_data.get("alerts", [])
            if language == "bn":
                loc_bn = {"Kolkata": "কলকাতা", "Nadia": "নদীয়া", "Darjeeling": "দার্জিলিং", "South 24 Parganas": "দক্ষিণ ২৪ পরগনা", "Delhi": "দিল্লি", "Mumbai": "মুম্বাই"}.get(loc_name, loc_name)
                alerts_text_bn = f" সতর্কতা: {alerts[0]['type']} - '{alerts[0]['message']}'" if alerts else " কোনো সক্রিয় দুর্যোগ সতর্কতা নেই।"

                if is_temp_query:
                    final_reply = (
                        f"আপডেট সময়: {timestamp_str} (উৎস: {source}), বর্তমানে **{loc_bn}-এর তাপমাত্রা {temp}°C** "
                        f"(আকাশ: {cond}, আর্দ্রতা: {humidity}%, বাতাসের গতি: {wind} মি/সে)।{alerts_text_bn}"
                    )
                elif is_wind_query:
                    final_reply = (
                        f"আপডেট সময়: {timestamp_str} (উৎস: {source}), বর্তমানে **{loc_bn}-এ বাতাসের গতিবেগ {wind} মি/সে** "
                        f"(আবহাওয়া: {cond}, তাপমাত্রা: {temp}°C)।{alerts_text_bn}"
                    )
                elif is_humidity_query:
                    final_reply = (
                        f"আপডেট সময়: {timestamp_str} (উৎস: {source}), বর্তমানে **{loc_bn}-এ আপেক্ষিক আর্দ্রতা {humidity}%** "
                        f"(তাপমাত্রা: {temp}°C, আকাশ: {cond})।{alerts_text_bn}"
                    )
                elif is_alert_query:
                    if alerts:
                        final_reply = (
                            f"⚠️ **{loc_bn}-এর জন্য সক্রিয় দুর্যোগ সতর্কতা**: {alerts[0]['type']} - '{alerts[0]['message']}' "
                            f"(উৎস: {alerts[0]['source']}, সময়: {timestamp_str})। অনুগ্রহ করে সতর্ক থাকুন।"
                        )
                    else:
                        final_reply = (
                            f"✅ **বর্তমানে {loc_bn}-এ কোনো সক্রিয় দুর্যোগ সতর্কতা নেই** (সময়: {timestamp_str}, উৎস: {source})। "
                            f"বর্তমান আবহাওয়া: {cond}, তাপমাত্রা: {temp}°C।"
                        )
                else:
                    final_reply = (
                        f"আপডেট সময়: {timestamp_str} (উৎস: {source}), বর্তমানে {loc_bn}-এর আবহাওয়া {cond}, "
                        f"তাপমাত্রা {temp}°C, আর্দ্রতা {humidity}% এবং বাতাসের গতিবেগ {wind} মি/সে।{alerts_text_bn}"
                    )

            elif language == "hi":
                loc_hi = {"Kolkata": "कोलकाता", "Nadia": "नादिया", "Darjeeling": "दार्जिलिंग", "South 24 Parganas": "दक्षिण 24 परगना", "Delhi": "दिल्ली", "Mumbai": "मुंबई"}.get(loc_name, loc_name)
                alerts_text_hi = f" चेतावनी: {alerts[0]['type']} - '{alerts[0]['message']}'" if alerts else " कोई सक्रिय मौसम चेतावनी नहीं है।"

                if is_temp_query:
                    final_reply = (
                        f"ताजा अपडेट: {timestamp_str} (स्रोत: {source}), वर्तमान में **{loc_hi} का तापमान {temp}°C** है "
                        f"(मौसम: {cond}, आर्द्रता: {humidity}%, हवा: {wind} मी/से)।{alerts_text_hi}"
                    )
                elif is_wind_query:
                    final_reply = (
                        f"ताजा अपडेट: {timestamp_str} (स्रोत: {source}), वर्तमान में **{loc_hi} में हवा की गति {wind} मी/से** है "
                        f"(मौसम: {cond}, तापमान: {temp}°C)।{alerts_text_hi}"
                    )
                elif is_humidity_query:
                    final_reply = (
                        f"ताजा अपडेट: {timestamp_str} (स्रोत: {source}), वर्तमान में **{loc_hi} में आर्द्रता {humidity}%** है "
                        f"(तापमान: {temp}°C, मौसम: {cond})।{alerts_text_hi}"
                    )
                elif is_alert_query:
                    if alerts:
                        final_reply = (
                            f"⚠️ **{loc_hi} के लिए सक्रिय मौसम चेतावनी**: {alerts[0]['type']} - '{alerts[0]['message']}' "
                            f"(स्रोत: {alerts[0]['source']}, समय: {timestamp_str})। कृपया सतर्क रहें।"
                        )
                    else:
                        final_reply = (
                            f"✅ **वर्तमान में {loc_hi} में कोई सक्रिय मौसम चेतावनी नहीं है** (समय: {timestamp_str}, स्रोत: {source})। "
                            f"वर्तमान मौसम: {cond}, तापमान: {temp}°C।"
                        )
                else:
                    final_reply = (
                        f"ताजा अपडेट: {timestamp_str} (स्रोत: {source}), वर्तमान में {loc_hi} का मौसम {cond} है, "
                        f"तापमान {temp}°C, आर्द्रता {humidity}% और हवा की गति {wind} मी/से है।{alerts_text_hi}"
                    )

            else:
                alerts_text = ""
                if alerts:
                    alerts_text = f" Active Warning: {alerts[0]['type']} - '{alerts[0]['message']}' ({alerts[0]['source']})."
                else:
                    alerts_text = " No active weather warnings are in effect."

                if is_temp_query:
                    final_reply = (
                        f"As of {timestamp_str} (Source: {source}), the current temperature in {loc_name} is "
                        f"**{temp}°C** with {cond.lower()} skies (Humidity: {humidity}%, Wind: {wind} m/s).{alerts_text}"
                    )
                elif is_wind_query:
                    final_reply = (
                        f"As of {timestamp_str} (Source: {source}), the wind speed in {loc_name} is "
                        f"**{wind} m/s** under {cond.lower()} conditions (Temp: {temp}°C).{alerts_text}"
                    )
                elif is_humidity_query:
                    final_reply = (
                        f"As of {timestamp_str} (Source: {source}), the relative humidity in {loc_name} is "
                        f"**{humidity}%** with {cond.lower()} skies and temperature of {temp}°C.{alerts_text}"
                    )
                elif is_alert_query:
                    if alerts:
                        final_reply = (
                            f"⚠️ **Active Weather Warning for {loc_name}**: {alerts[0]['type']} - '{alerts[0]['message']}' "
                            f"(Source: {alerts[0]['source']}, Timestamp: {timestamp_str}). Please exercise necessary precautions."
                        )
                    else:
                        final_reply = (
                            f"✅ **No active weather warnings** are currently in effect for {loc_name} as of {timestamp_str} (Source: {source}). "
                            f"Current weather is {cond} at {temp}°C."
                        )
                else:
                    final_reply = (
                        f"As of {timestamp_str} (Source: {source}), the weather in {loc_name} is "
                        f"{cond} with a temperature of {temp}°C, humidity at {humidity}%, and wind speeds of {wind} m/s.{alerts_text}"
                    )

        # Store assistant final answer
        db_final = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=final_reply,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        self.db.add(db_final)
        await self.db.commit()

        return final_reply
