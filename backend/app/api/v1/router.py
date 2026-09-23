from fastapi import APIRouter
from app.api.v1.endpoints import health, weather, locations, chat, alerts, voice, auth

api_router = APIRouter()

# Health endpoints
api_router.include_router(health.router, tags=["Health"])

# Authentication endpoints (/auth/signup, /auth/signin, /auth/me, /auth/users)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Weather endpoints (/weather/current, /weather/forecast)
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"])

# Location search endpoints (/locations/search)
api_router.include_router(locations.router, prefix="/locations", tags=["Locations"])

# Chat endpoint (/chat)
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Alerts endpoints (/alerts/ingest, /alerts/active, /alerts/ws/alerts)
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])

# Voice endpoints (/voice/transcribe, /voice/synthesize)
api_router.include_router(voice.router, prefix="/voice", tags=["Voice"])
