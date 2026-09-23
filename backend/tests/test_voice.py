import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_voice_synthesize_bengali(client: AsyncClient):
    """Verify POST /voice/synthesize returns valid MP3 audio for Bengali text."""
    res = await client.post(
        "/voice/synthesize",
        json={"text": "কাল বৃষ্টি হবে?", "language": "bn"},
    )
    assert res.status_code == 200
    assert "audio/mpeg" in res.headers.get("content-type", "")
    assert len(res.content) > 1000  # Valid MP3 binary payload


@pytest.mark.asyncio
async def test_voice_synthesize_hindi(client: AsyncClient):
    """Verify POST /voice/synthesize returns valid MP3 audio for Hindi text."""
    res = await client.post(
        "/voice/synthesize",
        json={"text": "कल बारिश होगी?", "language": "hi"},
    )
    assert res.status_code == 200
    assert "audio/mpeg" in res.headers.get("content-type", "")
    assert len(res.content) > 1000


@pytest.mark.asyncio
async def test_voice_transcribe_endpoint(client: AsyncClient):
    """Verify POST /voice/transcribe accepts audio and returns language + transcript."""
    fake_audio = b"RIFF....WAVEfmt ...."
    files = {"file": ("test_bengali_sample.wav", fake_audio, "audio/wav")}
    res = await client.post("/voice/transcribe", files=files)
    assert res.status_code == 200
    data = res.json()
    assert "transcript" in data
    assert data.get("language") == "bn"


@pytest.mark.asyncio
async def test_chat_bengali_exit_check(client: AsyncClient):
    """Exit check: Asking 'কাল বৃষ্টি হবে?' gets a correct Bengali response."""
    res = await client.post(
        "/chat",
        json={
            "message": "কাল বৃষ্টি হবে?",
            "session_id": "test_session_bn_exit",
            "lat": 22.5726,
            "lon": 88.3639,
            "language": "bn",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data.get("language") == "bn"
    reply = data.get("reply", "")
    assert "পূর্বাভাস" in reply or "কলকাতা" in reply or "বৃষ্টি" in reply
    assert "OpenWeather" in reply


@pytest.mark.asyncio
async def test_chat_hindi_query(client: AsyncClient):
    """Verify Hindi chat query returns grounded Hindi response."""
    res = await client.post(
        "/chat",
        json={
            "message": "कल बारिश होगी?",
            "session_id": "test_session_hi_exit",
            "lat": 28.6139,
            "lon": 77.2090,
            "language": "hi",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data.get("language") == "hi"
    reply = data.get("reply", "")
    assert "पूर्वानুमान" in reply or "पूर्वानुमान" in reply or "बारिश" in reply or "मौसम" in reply
