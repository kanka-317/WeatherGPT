import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine, Base
from app.models.weather import Location, WeatherObservation, Alert

DEMO_CITIES = [
    {
        "name": "Kolkata",
        "lat": 22.5726,
        "lon": 88.3639,
        "state": "West Bengal",
        "country": "IN",
        "temp": 32.4,
        "humidity": 78.0,
        "rainfall": 1.2,
        "wind_speed": 4.1,
        "wind_direction": 160.0,
        "condition": "Humid / Haze",
        "alert": {
            "type": "Thunderstorm Watch",
            "severity": "Moderate",
            "message": "Scattered thundershowers with lightning and gusty winds (30-40 kmph) expected over Kolkata.",
            "source": "IMD Regional Meteorological Centre Alipore",
        },
    },
    {
        "name": "Delhi",
        "lat": 28.6139,
        "lon": 77.2090,
        "state": "Delhi",
        "country": "IN",
        "temp": 34.2,
        "humidity": 52.0,
        "rainfall": 0.0,
        "wind_speed": 3.8,
        "wind_direction": 270.0,
        "condition": "Sunny",
    },
    {
        "name": "Mumbai",
        "lat": 19.0760,
        "lon": 72.8777,
        "state": "Maharashtra",
        "country": "IN",
        "temp": 30.1,
        "humidity": 84.0,
        "rainfall": 4.5,
        "wind_speed": 6.2,
        "wind_direction": 220.0,
        "condition": "Scattered Rain",
    },
    {
        "name": "Chennai",
        "lat": 13.0827,
        "lon": 80.2707,
        "state": "Tamil Nadu",
        "country": "IN",
        "temp": 31.8,
        "humidity": 80.0,
        "rainfall": 0.0,
        "wind_speed": 4.5,
        "wind_direction": 110.0,
        "condition": "Partly Cloudy",
    },
    {
        "name": "Nadia",
        "lat": 23.4710,
        "lon": 88.5565,
        "state": "West Bengal",
        "country": "IN",
        "temp": 31.0,
        "humidity": 79.0,
        "rainfall": 0.8,
        "wind_speed": 3.2,
        "wind_direction": 170.0,
        "condition": "Passing Showers",
        "alert": {
            "type": "Agro-Meteorological Advisory",
            "severity": "Advisory",
            "message": "Farmers in Nadia district advised to complete jute retting and drain standing water from vegetable nurseries.",
            "source": "IMD Gramin Krishi Mausam Sewa",
        },
    },
    {
        "name": "Bengaluru",
        "lat": 12.9716,
        "lon": 77.5946,
        "state": "Karnataka",
        "country": "IN",
        "temp": 26.5,
        "humidity": 68.0,
        "rainfall": 0.0,
        "wind_speed": 4.8,
        "wind_direction": 250.0,
        "condition": "Pleasant / Breeze",
    },
    {
        "name": "Hyderabad",
        "lat": 17.3850,
        "lon": 78.4867,
        "state": "Telangana",
        "country": "IN",
        "temp": 30.8,
        "humidity": 64.0,
        "rainfall": 0.0,
        "wind_speed": 3.9,
        "wind_direction": 190.0,
        "condition": "Partly Cloudy",
    },
]


async def seed_database():
    """Seed major Indian cities and initial weather observations into the database."""
    print("Beginning database seed for Indian cities (Phase 1)...")
    async with AsyncSessionLocal() as session:
        # Create tables if not already present (fallback safe)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        now = datetime.utcnow()

        for city_data in DEMO_CITIES:
            # Check if city already exists
            stmt = select(Location).where(Location.name == city_data["name"])
            res = await session.execute(stmt)
            loc = res.scalars().first()

            if loc is None:
                loc = Location(
                    name=city_data["name"],
                    lat=city_data["lat"],
                    lon=city_data["lon"],
                    state=city_data["state"],
                    country=city_data["country"],
                )
                session.add(loc)
                await session.flush()
                await session.refresh(loc)
                print(f"  + Added location: {loc.name} ({loc.lat}, {loc.lon})")
            else:
                print(f"  * Existing location: {loc.name}")

            # Add fresh observation
            obs = WeatherObservation(
                location_id=loc.id,
                temperature=city_data["temp"],
                humidity=city_data["humidity"],
                rainfall=city_data["rainfall"],
                wind_speed=city_data["wind_speed"],
                wind_direction=city_data["wind_direction"],
                condition=city_data["condition"],
                source="openweather_cached_seed",
                timestamp=now,
            )
            session.add(obs)

            # Add alert if present
            if "alert" in city_data:
                alert_data = city_data["alert"]
                alert = Alert(
                    location_id=loc.id,
                    type=alert_data["type"],
                    severity=alert_data["severity"],
                    message=alert_data["message"],
                    source=alert_data["source"],
                    valid_from=now,
                    valid_until=now + timedelta(hours=24),
                )
                session.add(alert)

        await session.commit()
        print("Database seed completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_database())
