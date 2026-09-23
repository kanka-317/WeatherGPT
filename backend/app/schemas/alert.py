from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AlertIngestRequest(BaseModel):
    location_name: str = Field(..., description="Target city, district, or region (e.g. 'Nadia', 'Kolkata')")
    type: str = Field(..., description="Alert type (e.g. 'Heavy Rain Warning', 'Thunderstorm Watch', 'Flash Flood Alert')")
    severity: str = Field(..., description="Severity level: 'Low', 'Moderate', 'Severe', or 'Extreme'")
    message: str = Field(..., description="Official meteorological or agro-disaster advisory message")
    valid_from: Optional[datetime] = Field(default=None, description="Start timestamp. Defaults to UTC now")
    valid_until: datetime = Field(..., description="Expiration timestamp")
    lat: Optional[float] = Field(default=None, description="Optional explicit latitude coordinate")
    lon: Optional[float] = Field(default=None, description="Optional explicit longitude coordinate")
    source: str = Field(default="IMD", description="Issuing meteorological agency or authority")


class AlertDetailResponse(BaseModel):
    id: int
    location_id: int
    location_name: str
    lat: float
    lon: float
    type: str
    severity: str
    message: str
    source: str
    valid_from: datetime
    valid_until: datetime
    distance_km: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ActiveAlertsResponse(BaseModel):
    total: int
    radius_km: Optional[float] = None
    center: Optional[dict] = None
    alerts: List[AlertDetailResponse]
