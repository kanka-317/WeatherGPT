from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, AsyncSessionLocal
from app.models.weather import Location, Alert
from app.schemas.alert import AlertIngestRequest, AlertDetailResponse, ActiveAlertsResponse
from app.services.alert_manager import ws_manager, get_active_alerts_spatial
from app.services.weather_service import WeatherService

router = APIRouter()


@router.post(
    "/ingest",
    response_model=AlertDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Manually trigger an official alert (live demo trigger)",
)
async def ingest_alert(
    payload: AlertIngestRequest,
    db: AsyncSession = Depends(get_db),
) -> AlertDetailResponse:
    """Manually ingest an official weather alert or agro-disaster warning.
    
    1. Resolves or creates the location coordinates.
    2. Persists the alert to the database.
    3. Broadcasts the alert in real-time to all active WebSocket clients.
    """
    service = WeatherService(db=db)

    # 1. Resolve coordinates if not explicitly passed
    lat, lon = payload.lat, payload.lon
    if lat is None or lon is None:
        geocoded = await service.geocode(payload.location_name)
        if geocoded:
            lat = geocoded[0].lat
            lon = geocoded[0].lon
        else:
            # Default fallback for demonstration
            lat, lon = 23.4710, 88.5565

    # 2. Get or create location record
    loc = await service.get_or_create_location(lat=lat, lon=lon, name_hint=payload.location_name)

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    valid_from = payload.valid_from.replace(tzinfo=None) if payload.valid_from else now
    valid_until = payload.valid_until.replace(tzinfo=None) if payload.valid_until else None

    # 3. Create Alert in DB
    new_alert = Alert(
        location_id=loc.id,
        type=payload.type,
        severity=payload.severity,
        message=payload.message,
        source=payload.source,
        valid_from=valid_from,
        valid_until=valid_until,
    )
    db.add(new_alert)
    await db.commit()
    await db.refresh(new_alert)

    alert_response = AlertDetailResponse(
        id=new_alert.id,
        location_id=loc.id,
        location_name=loc.name,
        lat=loc.lat,
        lon=loc.lon,
        type=new_alert.type,
        severity=new_alert.severity,
        message=new_alert.message,
        source=new_alert.source,
        valid_from=new_alert.valid_from,
        valid_until=new_alert.valid_until,
        distance_km=0.0,
    )

    # 4. Broadcast live alert over WebSockets to connected browsers/dashboards
    broadcast_payload = {
        "event": "NEW_ALERT",
        "alert": {
            **alert_response.model_dump(),
            "valid_from": alert_response.valid_from.isoformat(),
            "valid_until": alert_response.valid_until.isoformat(),
        },
        "timestamp": now.isoformat(),
    }
    await ws_manager.broadcast(broadcast_payload)

    return alert_response


@router.get(
    "/active",
    response_model=ActiveAlertsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get active alerts with optional PostGIS spatial radius filter",
)
async def get_active_alerts(
    lat: Optional[float] = Query(default=None, description="Latitude center point"),
    lon: Optional[float] = Query(default=None, description="Longitude center point"),
    radius_km: Optional[float] = Query(default=50.0, description="Spatial search radius in km"),
    db: AsyncSession = Depends(get_db),
) -> ActiveAlertsResponse:
    """Retrieve active alerts. If coordinates are provided, uses PostGIS ST_DWithin
    to find alerts within radius_km. Otherwise, returns all active alerts.
    """
    alerts = await get_active_alerts_spatial(
        db=db,
        lat=lat,
        lon=lon,
        radius_km=radius_km if (lat is not None and lon is not None) else None,
    )

    center_dict = {"lat": lat, "lon": lon} if (lat is not None and lon is not None) else None

    return ActiveAlertsResponse(
        total=len(alerts),
        radius_km=radius_km if center_dict else None,
        center=center_dict,
        alerts=alerts,
    )


@router.delete(
    "/{alert_id}",
    status_code=status.HTTP_200_OK,
    summary="Dismiss/delete an active alert bulletin",
)
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an alert by ID and broadcast updated state to all connected dashboards."""
    alert = await db.get(Alert, alert_id)
    if alert:
        await db.delete(alert)
        await db.commit()

    active_alerts = await get_active_alerts_spatial(db=db)
    serialized = [
        {
            **a.model_dump(),
            "valid_from": a.valid_from.isoformat(),
            "valid_until": a.valid_until.isoformat(),
        }
        for a in active_alerts
    ]
    await ws_manager.broadcast({
        "event": "INIT_SNAPSHOT",
        "total": len(serialized),
        "alerts": serialized,
    })
    return {"status": "deleted", "id": alert_id}


@router.post(
    "/clear-demo",
    status_code=status.HTTP_200_OK,
    summary="Clear all active alert bulletins (Demo Reset)",
)
async def clear_demo_alerts(db: AsyncSession = Depends(get_db)):
    """Reset the alert feed and push update to all connected WebSocket clients."""
    from sqlalchemy import delete

    await db.execute(delete(Alert))
    await db.commit()
    await ws_manager.broadcast({
        "event": "INIT_SNAPSHOT",
        "total": 0,
        "alerts": [],
    })
    return {"status": "cleared"}


# WebSocket endpoint for real-time alert push
@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """Real-time WebSocket feed streaming live alerts as they are ingested."""
    await ws_manager.connect(websocket)
    try:
        # Send initial snapshot of currently active alerts on connect
        async with AsyncSessionLocal() as session:
            active_alerts = await get_active_alerts_spatial(db=session)
            serialized_alerts = [
                {
                    **a.model_dump(),
                    "valid_from": a.valid_from.isoformat(),
                    "valid_until": a.valid_until.isoformat(),
                }
                for a in active_alerts
            ]
            await websocket.send_json({
                "event": "INIT_SNAPSHOT",
                "total": len(serialized_alerts),
                "alerts": serialized_alerts,
            })

        # Keep connection open and handle incoming ping/messages
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket] Disconnect or error: {e}")
        ws_manager.disconnect(websocket)
