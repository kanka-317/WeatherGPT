from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_direct_weather_question(client: AsyncClient):
    """Test direct weather question with location (Kolkata)."""
    payload = {
        "message": "What is the weather in Kolkata?",
        "session_id": "session-test-01",
    }
    response = await client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["session_id"] == "session-test-01"
    assert "reply" in data
    assert "Kolkata" in data["reply"]
    assert "OpenWeather" in data["reply"] or "source" in data["reply"].lower()
    assert "as of" in data["reply"].lower()
    assert "get_current_weather" in data["tools_called"]


@pytest.mark.asyncio
async def test_chat_forecast_grounded_exit_check(client: AsyncClient):
    """Exit check: /chat with 'Will it rain in Kolkata tomorrow?' returns a grounded answer
    citing real forecast data, not a hallucinated one.
    """
    payload = {
        "message": "Will it rain in Kolkata tomorrow?",
        "session_id": "session-test-02",
    }
    response = await client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["session_id"] == "session-test-02"
    assert "get_forecast" in data["tools_called"]
    # Check grounded content
    reply = data["reply"]
    assert "Kolkata" in reply
    assert "tomorrow" in reply.lower()
    assert "OpenWeather" in reply or "IMD" in reply
    assert "as of" in reply.lower()
    # Ensure it mentions rain or precipitation value
    assert "rain" in reply.lower() or "mm" in reply.lower()


@pytest.mark.asyncio
async def test_chat_farmer_advisory(client: AsyncClient):
    """Test farmer advisory question ('Should I irrigate my crops in Nadia tomorrow?')."""
    payload = {
        "message": "Should I irrigate my crops in Nadia tomorrow?",
        "session_id": "session-test-03",
    }
    response = await client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["session_id"] == "session-test-03"
    assert "get_forecast" in data["tools_called"]
    reply = data["reply"]
    assert "Nadia" in reply
    assert "irriga" in reply.lower()  # irrigating / irrigation
    assert "as of" in reply.lower()


@pytest.mark.asyncio
async def test_chat_no_location_triggers_clarification(client: AsyncClient):
    """Test that a query without location asks clarifying question instead of guessing."""
    payload = {
        "message": "Will it rain tomorrow?",
        "session_id": "session-test-04",
    }
    response = await client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["session_id"] == "session-test-04"
    assert len(data["tools_called"]) == 0
    reply = data["reply"].lower()
    assert "which" in reply or "location" in reply or "city" in reply


@pytest.mark.asyncio
async def test_chat_session_history_persistence(client: AsyncClient):
    """Verify chat messages (user, tool, assistant) are saved and queryable by session_id."""
    session_id = "session-test-persist-99"
    payload = {
        "message": "What is the weather in Delhi?",
        "session_id": session_id,
    }
    res_chat = await client.post("/chat", json=payload)
    assert res_chat.status_code == 200

    # Retrieve history
    res_hist = await client.get(f"/chat/history?session_id={session_id}")
    assert res_hist.status_code == 200
    history = res_hist.json()

    assert len(history) >= 2  # user + assistant (+ tool)
    roles = [m["role"] for m in history]
    assert "user" in roles
    assert "assistant" in roles
    assert history[0]["content"] == "What is the weather in Delhi?"
