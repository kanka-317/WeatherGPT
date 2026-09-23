from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# Location Schemas
class LocationBase(BaseModel):
    name: str
    lat: float
    lon: float
    state: Optional[str] = None
    country: str = "IN"


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Weather Observation Schemas
class WeatherObservationBase(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage (0-100)")
    rainfall: float = Field(default=0.0, description="Precipitation in mm")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_direction: Optional[float] = Field(default=None, description="Wind direction in degrees")
    condition: str = Field(..., description="Weather condition description (e.g. Clear, Rain)")
    source: str = Field(default="openweather", description="Data provider source")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WeatherObservationResponse(WeatherObservationBase):
    id: int
    location_id: int

    model_config = ConfigDict(from_attributes=True)


# Alert Schemas
class AlertBase(BaseModel):
    type: str
    severity: str
    message: str
    source: str = "imd"
    valid_from: datetime
    valid_until: datetime


class AlertResponse(AlertBase):
    id: int
    location_id: int

    model_config = ConfigDict(from_attributes=True)


# Current Weather Combined Response
class CurrentWeatherResponse(BaseModel):
    location: LocationBase
    observation: WeatherObservationBase
    cached: bool = Field(..., description="True if served from the 15-minute database cache")
    cache_age_seconds: Optional[int] = Field(default=0, description="Age of cached record in seconds")
    alerts: List[AlertResponse] = Field(default_factory=list)


# Forecast Schemas
class ForecastItem(BaseModel):
    timestamp: datetime
    temperature: float
    feels_like: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    humidity: float
    rainfall: float = 0.0
    wind_speed: float
    condition: str
    description: Optional[str] = None
    icon: Optional[str] = None


class ForecastResponse(BaseModel):
    location: LocationBase
    forecast: List[ForecastItem]
    count: int
