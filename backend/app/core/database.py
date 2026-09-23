import socket
from typing import AsyncGenerator
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Determine database URL: if db host 'db' is unreachable (running on local host outside Docker), fall back to SQLite
db_url = settings.DATABASE_URL
parsed = urlparse(db_url)
if parsed.hostname == "db":
    try:
        socket.getaddrinfo("db", parsed.port or 5432)
    except socket.gaierror:
        db_url = "sqlite+aiosqlite:///./weathergpt_local.db"

# Configure async engine
connect_args = {}
if "sqlite" in db_url:
    connect_args["check_same_thread"] = False
elif "supabase" in db_url or "ssl=require" in db_url:
    connect_args["ssl"] = "require"

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
