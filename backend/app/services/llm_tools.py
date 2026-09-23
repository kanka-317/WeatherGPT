from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from sqlalchemy import select, and_

from app.models.weather import Location, Alert
from app.services.weather_service import WeatherService

WEATHER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get current weather observations (temperature, humidity, wind, rainfall, conditions) for a given location or coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location_name": {
                        "type": "string",
                        "description": "City or district name (e.g. 'Kolkata', 'Delhi', 'Nadia')."
                    },
                    "lat": {
                        "type": "number",
                        "description": "Latitude coordinate."
                    },
                    "lon": {
                        "type": "number",
                        "description": "Longitude coordinate."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_forecast",
            "description": "Get multi-day weather forecast (up to 5 days, 3-hour intervals) including expected rainfall, temperature highs/lows, and conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location_name": {
                        "type": "string",
                        "description": "City or district name (e.g. 'Kolkata', 'Nadia')."
                    },
                    "lat": {
                        "type": "number",
                        "description": "Latitude coordinate."
                    },
                    "lon": {
                        "type": "number",
                        "description": "Longitude coordinate."
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days for forecast (1-5). Default is 5.",
                        "default": 5
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_alerts",
            "description": "Get active official government weather alerts, agro-meteorological advisories, or storm warnings for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location_name": {
                        "type": "string",
                        "description": "City or district name (e.g. 'Kolkata', 'Nadia')."
                    },
                    "lat": {
                        "type": "number",
                        "description": "Latitude coordinate."
                    },
                    "lon": {
                        "type": "number",
                        "description": "Longitude coordinate."
                    }
                },
                "required": []
            }
        }
    }
]


async def resolve_coordinates(
    weather_service: WeatherService,
    location_name: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    default_lat: Optional[float] = None,
    default_lon: Optional[float] = None,
) -> tuple[Optional[float], Optional[float], Optional[str]]:
    """Resolve (lat, lon, resolved_name) from explicit coordinates or geocoding."""
    if lat is not None and lon is not None:
        return lat, lon, location_name

    if location_name:
        locs = await weather_service.geocode(location_name)
        if locs:
            return locs[0].lat, locs[0].lon, locs[0].name

    if default_lat is not None and default_lon is not None:
        return default_lat, default_lon, location_name or f"({default_lat:.2f}, {default_lon:.2f})"

    return None, None, None


async def execute_tool_call(
    name: str,
    arguments: Dict[str, Any],
    weather_service: WeatherService,
    default_lat: Optional[float] = None,
    default_lon: Optional[float] = None,
) -> Dict[str, Any]:
    """Execute the requested tool against internal WeatherService and database."""
    loc_name = arguments.get("location_name")
    lat_arg = arguments.get("lat")
    lon_arg = arguments.get("lon")

    lat, lon, resolved_name = await resolve_coordinates(
        weather_service,
        location_name=loc_name,
        lat=lat_arg,
        lon=lon_arg,
        default_lat=default_lat,
        default_lon=default_lon,
    )

    if lat is None or lon is None:
        return {
            "error": "Missing location",
            "message": f"Could not determine latitude and longitude for '{loc_name or 'unspecified location'}'. Ask user to provide location."
        }

    if name == "get_current_weather":
        current_res = await weather_service.get_current_weather(lat=lat, lon=lon)
        return {
            "location": current_res.location.model_dump(),
            "observation": {
                **current_res.observation.model_dump(),
                "timestamp": current_res.observation.timestamp.isoformat(),
            },
            "cached": current_res.cached,
            "cache_age_seconds": current_res.cache_age_seconds,
            "alerts": [a.model_dump() for a in current_res.alerts],
        }

    elif name == "get_forecast":
        days = int(arguments.get("days", 5))
        forecast_res = await weather_service.get_forecast(lat=lat, lon=lon, days=days)
        loc_dict = forecast_res.location.model_dump()
        if resolved_name and (loc_dict.get("name", "").startswith("Coord (") or loc_dict.get("name", "").startswith("Location (")):
            loc_dict["name"] = resolved_name
        # Convert datetime objects to string format for JSON serialization
        items = []
        for item in forecast_res.forecast:
            d = item.model_dump()
            d["timestamp"] = item.timestamp.isoformat()
            items.append(d)
        return {
            "location": loc_dict,
            "count": forecast_res.count,
            "forecast": items,
        }

    elif name == "get_active_alerts":
        from app.services.alert_manager import get_active_alerts_spatial
        spatial_alerts = await get_active_alerts_spatial(
            db=weather_service.db,
            lat=lat,
            lon=lon,
            radius_km=50.0,
        )
        return {
            "location": {"name": resolved_name or f"({lat:.2f}, {lon:.2f})", "lat": lat, "lon": lon},
            "alerts_count": len(spatial_alerts),
            "alerts": [
                {
                    "id": a.id,
                    "location_name": a.location_name,
                    "type": a.type,
                    "severity": a.severity,
                    "message": a.message,
                    "source": a.source,
                    "valid_from": a.valid_from.isoformat(),
                    "valid_until": a.valid_until.isoformat(),
                    "distance_km": a.distance_km,
                }
                for a in spatial_alerts
            ],
        }

    return {"error": f"Unknown tool name '{name}'."}
