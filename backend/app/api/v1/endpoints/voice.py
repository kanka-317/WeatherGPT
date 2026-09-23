from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import Response

from app.schemas.voice import TranscriptionResponse, SynthesizeRequest
from app.services.voice_service import voice_service

router = APIRouter()


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe audio file into text using OpenAI Whisper API",
)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file (wav, webm, mp3, m4a)"),
) -> TranscriptionResponse:
    """Accepts an audio file, transcribes speech with Whisper, and detects the language."""
    audio_bytes = await file.read()
    filename = file.filename or "audio.wav"
    content_type = file.content_type or "audio/wav"

    return await voice_service.transcribe(
        audio_bytes=audio_bytes,
        filename=filename,
        content_type=content_type,
    )


@router.post(
    "/synthesize",
    status_code=status.HTTP_200_OK,
    summary="Synthesize text into speech audio (MP3)",
)
async def synthesize_speech(
    payload: SynthesizeRequest,
) -> Response:
    """Takes text + language (en/hi/bn) and returns streaming MP3 speech audio."""
    audio_bytes = await voice_service.synthesize(
        text=payload.text,
        language=payload.language,
    )

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=speech.mp3",
            "Cache-Control": "public, max-age=3600",
        },
    )
