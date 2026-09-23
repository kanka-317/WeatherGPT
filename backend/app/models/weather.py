import datetime
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    state = Column(String(100), nullable=True)
    country = Column(String(10), default="IN", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    observations = relationship("WeatherObservation", back_populates="location", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="location", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_location_lat_lon", "lat", "lon"),
    )

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, name='{self.name}', lat={self.lat}, lon={self.lon})>"


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    temperature = Column(Float, nullable=False)  # in Celsius
    humidity = Column(Float, nullable=False)     # percentage (0-100)
    rainfall = Column(Float, default=0.0, nullable=False)  # in mm
    wind_speed = Column(Float, nullable=False)   # in m/s or km/h
    wind_direction = Column(Float, nullable=True) # in degrees (0-360)
    condition = Column(String(100), nullable=False) # e.g. "Clear", "Rain", "Haze"
    source = Column(String(50), default="openweather", nullable=False) # "openweather", "imd", etc.
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    # Relationships
    location = relationship("Location", back_populates="observations")

    __table_args__ = (
        Index("idx_observation_loc_time", "location_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return (
            f"<WeatherObservation(id={self.id}, location_id={self.location_id}, "
            f"temp={self.temperature}, condition='{self.condition}', time='{self.timestamp}')>"
        )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(100), nullable=False)  # e.g. "Thunderstorm", "Heatwave", "Heavy Rain"
    severity = Column(String(50), nullable=False)  # e.g. "Warning", "Alert", "Watch", "Emergency"
    message = Column(Text, nullable=False)
    source = Column(String(50), default="imd", nullable=False)
    valid_from = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    valid_until = Column(DateTime, nullable=False)

    # Relationships
    location = relationship("Location", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type='{self.type}', severity='{self.severity}', location_id={self.location_id})>"
