from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from app.services.weather_provider import OpenWeatherProvider

MOCK_OPENWEATHER_CURRENT = {
    "coord": {"lon": 88.36, "lat": 22.57},
    "weather": [{"id": 721, "main": "Haze", "description": "haze", "icon": "50d"}],
    "main": {
        "temp": 32.5,
        "feels_like": 38.2,
        "temp_min": 31.0,
        "temp_max": 33.0,
        "pressure": 1008,
        "humidity": 75,
    },
    "visibility": 4000,
    "wind": {"speed": 3.6, "deg": 180},
    "rain": {"1h": 0.5},
    "clouds": {"all": 40},
    "dt": int(datetime.now(timezone.utc).timestamp()),
    "sys": {"country": "IN"},
    "name": "Kolkata",
}


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_current_weather_uncached_then_cached(client: AsyncClient):
    """Exit check verification: test fetching current weather for Kolkata coordinates (22.57, 88.36),
    verifying it's first fetched and stored, and subsequent query is served from the 15-minute DB cache.
    """
    # 1. First call: uncached
    res1 = await client.get("/weather/current?lat=22.57&lon=88.36")
    assert res1.status_code == 200
    data1 = res1.json()

    assert "location" in data1
    assert "observation" in data1
    assert data1["cached"] is False
    assert data1["observation"]["temperature"] > 0
    assert data1["observation"]["condition"] != ""
    assert data1["location"]["lat"] == 22.57
    assert data1["location"]["lon"] == 88.36

    # 2. Second call: should be served directly from PostgreSQL cache
    res2 = await client.get("/weather/current?lat=22.57&lon=88.36")
    assert res2.status_code == 200
    data2 = res2.json()

    assert data2["cached"] is True
    assert data2["cache_age_seconds"] >= 0
    assert data2["observation"]["temperature"] == data1["observation"]["temperature"]
    assert data2["observation"]["condition"] == data1["observation"]["condition"]


@pytest.mark.asyncio
async def test_current_weather_with_mocked_openweather(client: AsyncClient):
    """Test endpoint with mocked OpenWeatherProvider response."""
    with patch(
        "app.services.weather_provider.OpenWeatherProvider.get_current_weather",
        new_callable=AsyncMock,
    ) as mock_weather:
        mock_weather.return_value = {
            "location_name": "Kolkata",
            "lat": 22.58,
            "lon": 88.37,
            "temperature": 32.5,
            "humidity": 75.0,
            "rainfall": 0.5,
            "wind_speed": 3.6,
            "wind_direction": 180.0,
            "condition": "Haze",
            "source": "openweather",
            "timestamp": datetime.now(timezone.utc).replace(tzinfo=None),
        }

        # Use new coordinates to bypass previous cache
        lat, lon = 22.58, 88.37
        response = await client.get(f"/weather/current?lat={lat}&lon={lon}")
        assert response.status_code == 200
        data = response.json()

        assert data["cached"] is False
        assert data["observation"]["condition"] == "Haze"
        assert data["observation"]["temperature"] == 32.5
        assert data["observation"]["humidity"] == 75.0
        assert data["observation"]["rainfall"] == 0.5
        assert data["observation"]["source"] == "openweather"


def test_openweather_normalization_unit():
    """Unit test OpenWeatherProvider raw response normalization."""
    provider = OpenWeatherProvider(api_key="test_key")
    normalized = provider._normalize_current(MOCK_OPENWEATHER_CURRENT, lat=22.57, lon=88.36)

    assert normalized["location_name"] == "Kolkata"
    assert normalized["temperature"] == 32.5
    assert normalized["humidity"] == 75.0
    assert normalized["rainfall"] == 0.5
    assert normalized["wind_speed"] == 3.6
    assert normalized["condition"] == "Haze"
    assert normalized["source"] == "openweather"


@pytest.mark.asyncio
async def test_weather_forecast(client: AsyncClient):
    """Test multi-day forecast endpoint."""
    response = await client.get("/weather/forecast?lat=22.57&lon=88.36&days=3")
    assert response.status_code == 200
    data = response.json()

    assert "location" in data
    assert "forecast" in data
    assert len(data["forecast"]) > 0
    first_item = data["forecast"][0]
    assert "temperature" in first_item
    assert "condition" in first_item
    assert "timestamp" in first_item


@pytest.mark.asyncio
async def test_locations_search(client: AsyncClient):
    """Test geocoding place name search."""
    response = await client.get("/locations/search?q=Kolkata")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    kolkata = data[0]
    assert "Kolkata" in kolkata["name"]
    assert abs(kolkata["lat"] - 22.57) < 0.1
    assert abs(kolkata["lon"] - 88.36) < 0.1
