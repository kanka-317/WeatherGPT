from datetime import datetime, timedelta, timezone
import math
from typing import Any, Dict, List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather import Location, WeatherObservation, Alert
from app.schemas.weather import (
    LocationBase,
    WeatherObservationBase,
    CurrentWeatherResponse,
    ForecastResponse,
    AlertResponse,
)
from app.services.weather_provider import WeatherProvider, OpenWeatherProvider


CACHE_TTL_MINUTES = 15
COORD_PROXIMITY_THRESHOLD = 0.05  # roughly ~5km


class WeatherService:
    """Core weather service coordinating data providers, normalization, and PostgreSQL caching."""

    def __init__(self, db: AsyncSession, provider: Optional[WeatherProvider] = None):
        self.db = db
        self.provider = provider or OpenWeatherProvider()

    async def get_or_create_location(self, lat: float, lon: float, name_hint: Optional[str] = None) -> Location:
        """Find an existing location close to the coordinates or create a new one."""
        # Query for locations within threshold box
        stmt = (
            select(Location)
            .where(
                and_(
                    Location.lat.between(lat - COORD_PROXIMITY_THRESHOLD, lat + COORD_PROXIMITY_THRESHOLD),
                    Location.lon.between(lon - COORD_PROXIMITY_THRESHOLD, lon + COORD_PROXIMITY_THRESHOLD),
                )
            )
            .order_by(
                func.abs(Location.lat - lat) + func.abs(Location.lon - lon)
            )
            .limit(1)
        )
        result = await self.db.execute(stmt)
        location = result.scalars().first()

        if location is None:
            location = Location(
                name=name_hint or f"Location ({lat:.2f}, {lon:.2f})",
                lat=lat,
                lon=lon,
                country="IN",
            )
            self.db.add(location)
            await self.db.flush()
            await self.db.refresh(location)
        elif name_hint and (location.name.startswith("Location (") or location.name.startswith("Coord (")):
            # Update generic name with real name from provider
            location.name = name_hint
            await self.db.flush()

        return location

    async def get_current_weather(self, lat: float, lon: float) -> CurrentWeatherResponse:
        """Fetch current weather with a 15-minute PostgreSQL cache."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cache_cutoff = now - timedelta(minutes=CACHE_TTL_MINUTES)

        # 1. Resolve Location
        location = await self.get_or_create_location(lat, lon)

        # 2. Check for fresh cached observation
        obs_stmt = (
            select(WeatherObservation)
            .where(
                and_(
                    WeatherObservation.location_id == location.id,
                    WeatherObservation.timestamp >= cache_cutoff,
                )
            )
            .order_by(WeatherObservation.timestamp.desc())
            .limit(1)
        )
        obs_result = await self.db.execute(obs_stmt)
        cached_obs = obs_result.scalars().first()

        # 3. Check for active alerts
        alerts_stmt = (
            select(Alert)
            .where(
                and_(
                    Alert.location_id == location.id,
                    Alert.valid_until >= now,
                )
            )
        )
        alerts_res = await self.db.execute(alerts_stmt)
        alerts = alerts_res.scalars().all()
        alert_responses = [AlertResponse.model_validate(a) for a in alerts]

        if cached_obs:
            cache_age = int((now - cached_obs.timestamp).total_seconds())
            return CurrentWeatherResponse(
                location=LocationBase(
                    name=location.name,
                    lat=location.lat,
                    lon=location.lon,
                    state=location.state,
                    country=location.country,
                ),
                observation=WeatherObservationBase(
                    temperature=cached_obs.temperature,
                    humidity=cached_obs.humidity,
                    rainfall=cached_obs.rainfall,
                    wind_speed=cached_obs.wind_speed,
                    wind_direction=cached_obs.wind_direction,
                    condition=cached_obs.condition,
                    source=cached_obs.source,
                    timestamp=cached_obs.timestamp.replace(tzinfo=timezone.utc) if cached_obs.timestamp.tzinfo is None else cached_obs.timestamp,
                ),
                cached=True,
                cache_age_seconds=cache_age,
                alerts=alert_responses,
            )

        # 4. Fetch fresh from provider
        data = await self.provider.get_current_weather(lat, lon)

        # Update location name if provider gave a city name
        if data.get("location_name") and location.name.startswith("Location ("):
            location.name = data["location_name"]

        # 5. Persist to PostgreSQL
        raw_ts = data.get("timestamp", now)
        if isinstance(raw_ts, datetime) and raw_ts.tzinfo is not None:
            clean_ts = raw_ts.astimezone(timezone.utc).replace(tzinfo=None)
        elif isinstance(raw_ts, datetime):
            clean_ts = raw_ts
        else:
            clean_ts = now.replace(tzinfo=None) if hasattr(now, "tzinfo") and now.tzinfo is not None else now

        new_obs = WeatherObservation(
            location_id=location.id,
            temperature=data["temperature"],
            humidity=data["humidity"],
            rainfall=data.get("rainfall", 0.0),
            wind_speed=data["wind_speed"],
            wind_direction=data.get("wind_direction"),
            condition=data["condition"],
            source=data.get("source", "openweather"),
            timestamp=clean_ts,
        )
        self.db.add(new_obs)
        await self.db.commit()
        await self.db.refresh(new_obs)

        return CurrentWeatherResponse(
            location=LocationBase(
                name=location.name,
                lat=location.lat,
                lon=location.lon,
                state=location.state,
                country=location.country,
            ),
            observation=WeatherObservationBase(
                temperature=new_obs.temperature,
                humidity=new_obs.humidity,
                rainfall=new_obs.rainfall,
                wind_speed=new_obs.wind_speed,
                wind_direction=new_obs.wind_direction,
                condition=new_obs.condition,
                source=new_obs.source,
                timestamp=new_obs.timestamp.replace(tzinfo=timezone.utc) if new_obs.timestamp.tzinfo is None else new_obs.timestamp,
            ),
            cached=False,
            cache_age_seconds=0,
            alerts=alert_responses,
        )

    async def get_forecast(self, lat: float, lon: float, days: int = 5) -> ForecastResponse:
        """Fetch multi-day weather forecast."""
        data = await self.provider.get_forecast(lat, lon, days=days)
        return ForecastResponse.model_validate(data)

    async def geocode(self, query: str) -> List[LocationBase]:
        """Geocode search query and save/cache found locations in database."""
        results = await self.provider.geocode(query)
        locations = []
        for item in results:
            loc = await self.get_or_create_location(
                lat=item["lat"],
                lon=item["lon"],
                name_hint=item["name"],
            )
            if item.get("state") and not loc.state:
                loc.state = item["state"]
                await self.db.flush()
            locations.append(
                LocationBase(
                    name=loc.name,
                    lat=loc.lat,
                    lon=loc.lon,
                    state=loc.state,
                    country=loc.country,
                )
            )
        await self.db.commit()
        return locations
