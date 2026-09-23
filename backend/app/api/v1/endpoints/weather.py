from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.weather import CurrentWeatherResponse, ForecastResponse
from app.services.weather_service import WeatherService

router = APIRouter()


@router.get(
    "/current",
    response_model=CurrentWeatherResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current weather with 15-minute PostgreSQL caching",
)
async def get_current_weather(
    lat: float = Query(..., description="Latitude coordinate", ge=-90.0, le=90.0),
    lon: float = Query(..., description="Longitude coordinate", ge=-180.0, le=180.0),
    db: AsyncSession = Depends(get_db),
) -> CurrentWeatherResponse:
    """Fetch current weather for coordinates.
    
    Checks PostgreSQL for recent observations (within 15 minutes). If present,
    returns cached data with `cached: true`. If stale or absent, queries the
    provider (OpenWeather / IMD), stores in database, and returns `cached: false`.
    """
    service = WeatherService(db=db)
    return await service.get_current_weather(lat=lat, lon=lon)


@router.get(
    "/forecast",
    response_model=ForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="Get multi-day weather forecast",
)
async def get_forecast(
    lat: float = Query(..., description="Latitude coordinate", ge=-90.0, le=90.0),
    lon: float = Query(..., description="Longitude coordinate", ge=-180.0, le=180.0),
    days: int = Query(5, description="Number of forecast days (1-5)", ge=1, le=5),
    db: AsyncSession = Depends(get_db),
) -> ForecastResponse:
    """Fetch 5-day / 3-hour forecast for coordinates."""
    service = WeatherService(db=db)
    return await service.get_forecast(lat=lat, lon=lon, days=days)
