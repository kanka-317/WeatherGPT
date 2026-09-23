from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.weather import LocationBase
from app.services.weather_service import WeatherService

router = APIRouter()


@router.get(
    "/search",
    response_model=List[LocationBase],
    status_code=status.HTTP_200_OK,
    summary="Geocode place name to lat/lon coordinates",
)
async def search_locations(
    q: str = Query(..., min_length=1, description="Place name query (e.g. Kolkata, Delhi, Nadia)"),
    db: AsyncSession = Depends(get_db),
) -> List[LocationBase]:
    """Search for locations using OpenWeather geocoding API and cache discovered places in DB."""
    service = WeatherService(db=db)
    return await service.geocode(query=q)
