from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ingest_alert(client: AsyncClient):
    """Test POST /alerts/ingest successfully registers an alert and persists it."""
    payload = {
        "location_name": "Nadia",
        "lat": 23.4710,
        "lon": 88.5565,
        "type": "Heavy Rain Warning",
        "severity": "Severe",
        "message": "Heavy precipitation expected over Nadia district in next 24 hours.",
        "valid_until": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        "source": "IMD Alipore",
    }
    response = await client.post("/alerts/ingest", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["location_name"] == "Nadia"
    assert data["type"] == "Heavy Rain Warning"
    assert data["severity"] == "Severe"
    assert data["lat"] == 23.4710
    assert data["lon"] == 88.5565
    assert data["id"] > 0


@pytest.mark.asyncio
async def test_get_active_alerts_all(client: AsyncClient):
    """Test GET /alerts/active returns all currently active alerts."""
    # First ingest an alert
    await client.post("/alerts/ingest", json={
        "location_name": "Kolkata",
        "lat": 22.5726,
        "lon": 88.3639,
        "type": "Thunderstorm Watch",
        "severity": "Moderate",
        "message": "Moderate thunderstorm warning for Kolkata.",
        "valid_until": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        "source": "IMD",
    })

    response = await client.get("/alerts/active")
    assert response.status_code == 200
    data = response.json()

    assert "total" in data
    assert "alerts" in data
    assert isinstance(data["alerts"], list)
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_active_alerts_spatial_filter(client: AsyncClient):
    """Test GET /alerts/active with coordinates and radius."""
    # Ingest alert for Nadia
    await client.post("/alerts/ingest", json={
        "location_name": "Nadia",
        "lat": 23.4710,
        "lon": 88.5565,
        "type": "Heavy Rain Warning",
        "severity": "Severe",
        "message": "Heavy precipitation expected over Nadia district in next 24 hours.",
        "valid_until": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
        "source": "IMD Alipore",
    })

    # Query Nadia coordinates with 25 km radius
    response = await client.get("/alerts/active?lat=23.47&lon=88.55&radius_km=25")
    assert response.status_code == 200
    data = response.json()

    assert data["center"]["lat"] == 23.47
    assert data["radius_km"] == 25.0
    # Nadia alert should be included
    nadia_alerts = [a for a in data["alerts"] if a["location_name"] == "Nadia"]
    assert len(nadia_alerts) >= 1
    assert nadia_alerts[0]["distance_km"] < 25.0
