from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
from fastapi import WebSocket
from sqlalchemy import select, and_, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather import Location, Alert
from app.schemas.alert import AlertDetailResponse


class AlertWebSocketManager:
    """Manages connected WebSocket clients and broadcasts live alert notifications."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] Client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WebSocket] Client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WebSocket] Error broadcasting to client, removing: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            if dead in self.active_connections:
                self.active_connections.remove(dead)


# Global singleton instance for WebSocket broadcasting
ws_manager = AlertWebSocketManager()


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance between two points in km."""
    R = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


async def get_active_alerts_spatial(
    db: AsyncSession,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: Optional[float] = 50.0,
) -> List[AlertDetailResponse]:
    """Retrieve active alerts. If coordinates are provided, uses PostGIS ST_DWithin
    (or geodesic distance calculation) to return alerts within the radius.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # 1. Base query for active alerts joined with Location
    query = (
        select(Alert, Location)
        .join(Location, Alert.location_id == Location.id)
        .where(Alert.valid_until >= now)
        .order_by(Alert.valid_until.asc())
    )

    result = await db.execute(query)
    rows = result.all()

    alert_responses: List[AlertDetailResponse] = []

    for alert, location in rows:
        distance = None
        if lat is not None and lon is not None:
            # Calculate distance
            distance = round(haversine_distance_km(lat, lon, location.lat, location.lon), 2)
            # Filter by radius if requested
            if radius_km is not None and distance > radius_km:
                continue

        alert_responses.append(
            AlertDetailResponse(
                id=alert.id,
                location_id=alert.location_id,
                location_name=location.name,
                lat=location.lat,
                lon=location.lon,
                type=alert.type,
                severity=alert.severity,
                message=alert.message,
                source=alert.source,
                valid_from=alert.valid_from,
                valid_until=alert.valid_until,
                distance_km=distance,
            )
        )

    # If spatial search, order by closest distance
    if lat is not None and lon is not None:
        alert_responses.sort(key=lambda x: x.distance_km if x.distance_km is not None else 999999)

    return alert_responses
