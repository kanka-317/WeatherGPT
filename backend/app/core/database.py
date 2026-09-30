import socket
from typing import AsyncGenerator
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Determine database URL: sanitize driver prefix for asyncpg and support local fallback
db_url = settings.DATABASE_URL.strip().replace("\r", "").replace("\n", "")

# Normalize driver scheme for asyncpg (Supabase/Neon/Render often supply postgres:// or postgresql://)
if db_url.startswith("postgres://"):
    db_url = "postgresql+asyncpg://" + db_url[len("postgres://"):]
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = "postgresql+asyncpg://" + db_url[len("postgresql://"):]

# Remove sslmode query parameter if present because asyncpg does not accept it as a URL query param
if "sslmode=" in db_url:
    from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
    _u = urlsplit(db_url)
    _query_dict = dict(parse_qsl(_u.query))
    _query_dict.pop("sslmode", None)
    _new_query = urlencode(_query_dict)
    db_url = urlunsplit((_u.scheme, _u.netloc, _u.path, _new_query, _u.fragment))

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
elif "supabase" in db_url or "ssl=require" in db_url or parsed.hostname not in ("localhost", "127.0.0.1", "db"):
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
