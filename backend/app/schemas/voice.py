from typing import Optional
from pydantic import BaseModel, Field


class TranscriptionResponse(BaseModel):
    transcript: str = Field(..., description="Transcribed text from speech")
    language: str = Field(default="en", description="Detected language code (en, hi, bn)")
    confidence: Optional[float] = Field(default=None, description="Confidence score if available")


class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to convert into speech")
    language: str = Field(default="en", description="Target language code (en, hi, bn)")
