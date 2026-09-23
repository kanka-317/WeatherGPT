from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """Simple health check endpoint returning 200 OK."""
    return {"status": "ok"}


@router.get("/health/db", status_code=status.HTTP_200_OK)
async def db_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Database connectivity and extension verification endpoint."""
    try:
        # Check basic connection
        await db.execute(text("SELECT 1"))

        # Check PostGIS extension
        postgis_res = await db.execute(
            text("SELECT extversion FROM pg_extension WHERE extname = 'postgis'")
        )
        postgis_version = postgis_res.scalar()

        # Check pgvector extension
        vector_res = await db.execute(
            text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        )
        vector_version = vector_res.scalar()

        return {
            "status": "ok",
            "database": "connected",
            "extensions": {
                "postgis": {
                    "installed": postgis_version is not None,
                    "version": postgis_version or "not installed",
                },
                "pgvector": {
                    "installed": vector_version is not None,
                    "version": vector_version or "not installed",
                },
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database check failed: {str(e)}",
        )
