import asyncio
import io
import re
from typing import Optional
import openai
from gtts import gTTS

from app.core.config import settings
from app.schemas.voice import TranscriptionResponse


def clean_text_for_speech(text: str) -> str:
    """Strip markdown formatting, emojis, and asterisks for smooth TTS pronunciation."""
    # Remove markdown links [text](url) -> text
    cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove markdown bold/italic asterisks and underscores
    cleaned = re.sub(r'[*_~`#]', '', cleaned)
    # Remove multiple spaces/newlines
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


class VoiceService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.openai_quota_exhausted = False

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        content_type: str = "audio/wav",
    ) -> TranscriptionResponse:
        """Transcribe speech audio into text using OpenAI Whisper API with graceful fallback."""
        is_real_openai = (
            bool(self.api_key)
            and not self.api_key.startswith("your_")
            and self.api_key != "mock_or_real_openai_key"
            and not self.openai_quota_exhausted
        )

        if is_real_openai:
            try:
                client = openai.AsyncOpenAI(api_key=self.api_key)
                response = await asyncio.wait_for(
                    client.audio.transcriptions.create(
                        model="whisper-1",
                        file=(filename, audio_bytes, content_type),
                        response_format="verbose_json",
                    ),
                    timeout=25.0,
                )
                detected_lang = getattr(response, "language", "en")
                # Normalize language codes
                if detected_lang in ["bengali", "ben"]:
                    detected_lang = "bn"
                elif detected_lang in ["hindi", "hin"]:
                    detected_lang = "hi"
                elif detected_lang in ["english", "eng"]:
                    detected_lang = "en"

                transcript_text = getattr(response, "text", "").strip()
                if transcript_text:
                    return TranscriptionResponse(
                        transcript=transcript_text,
                        language=detected_lang if detected_lang in ["en", "hi", "bn"] else "en",
                    )
            except Exception as e:
                err_str = str(e).lower()
                if "insufficient_quota" in err_str or "429" in err_str:
                    self.openai_quota_exhausted = True
                print(f"[VoiceService] Whisper transcription error or quota exceeded: {e}")

        # Fallback transcription when OpenAI Whisper is unavailable or audio is silent
        return TranscriptionResponse(
            transcript="",
            language="en",
        )

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """Synthesize text into speech MP3 bytes.
        
        Attempts OpenAI TTS first; automatically falls back to gTTS for
        reliable Bengali (bn), Hindi (hi), and English (en) audio generation.
        """
        clean_text = clean_text_for_speech(text)
        if not clean_text:
            clean_text = "No content to read."

        lang = language.lower() if language else "en"
        if lang not in ["en", "hi", "bn"]:
            lang = "en"

        is_real_openai = (
            bool(self.api_key)
            and not self.api_key.startswith("your_")
            and self.api_key != "mock_or_real_openai_key"
            and not self.openai_quota_exhausted
        )

        if is_real_openai:
            try:
                client = openai.AsyncOpenAI(api_key=self.api_key)
                response = await asyncio.wait_for(
                    client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=clean_text,
                    ),
                    timeout=3.0,
                )
                return response.content
            except Exception as e:
                err_str = str(e).lower()
                if "insufficient_quota" in err_str or "429" in err_str:
                    self.openai_quota_exhausted = True
                print(f"[VoiceService] OpenAI TTS quota exceeded ({e}), falling back to gTTS.")

        # Reliable zero-cost gTTS fallback (native support for English, Hindi, Bengali)
        def _generate_gtts() -> bytes:
            tts = gTTS(text=clean_text, lang=lang, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()

        # Run synchronous gTTS in threadpool to avoid blocking event loop
        loop = asyncio.get_running_loop()
        audio_bytes = await loop.run_in_executor(None, _generate_gtts)
        return audio_bytes


# Global singleton instance
voice_service = VoiceService()
