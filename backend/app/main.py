from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.endpoints import weather, locations, chat, alerts, voice, auth
from app.services.alert_manager import ws_manager
from app.core.config import settings


from app.core.database import Base, engine
import app.models  # Ensure models are loaded for table creation

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup actions: ensure tables exist
    print(f"Starting {settings.PROJECT_NAME} backend...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown actions
    print(f"Shutting down {settings.PROJECT_NAME} backend...")


from fastapi.responses import RedirectResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="WeatherGPT: AI-Driven Meteorological Intelligence & Disaster Early-Warning System (SIH PS 26068)",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration: allow credentials for all origins (Netlify, Vercel, Render, local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )


# Root welcome endpoint
@app.get("/", tags=["Root"])
async def root():
    """Welcome and API documentation entry point."""
    return {
        "message": "Welcome to WeatherGPT API (SIH PS 26068)",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "health": "/health",
        "version": "1.0.0",
    }


# Backwards-compatibility redirect for /api/v1/docs
@app.get("/api/v1/docs", include_in_schema=False)
async def redirect_api_v1_docs():
    return RedirectResponse(url="/docs")


# Root level health endpoint
@app.get("/health", tags=["Health"])
async def root_health_check():
    """Root health endpoint."""
    return {"status": "ok"}


# Direct top-level routes for /weather, /locations, /chat, /alerts, and /voice
app.include_router(weather.router, prefix="/weather", tags=["Weather (Root)"])
app.include_router(locations.router, prefix="/locations", tags=["Locations (Root)"])
app.include_router(chat.router, prefix="/chat", tags=["Chat (Root)"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts (Root)"])
app.include_router(voice.router, prefix="/voice", tags=["Voice (Root)"])
app.include_router(auth.router, prefix="/auth", tags=["Auth (Root)"])

# Direct top-level WebSocket endpoint for live alert streaming
app.add_api_websocket_route("/ws/alerts", alerts.websocket_alerts_endpoint)

# Standard versioned API v1 router (/api/v1/...)
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
