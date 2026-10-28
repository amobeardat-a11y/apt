from typing import AsyncGenerator
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

def normalize_database_url(url: str) -> tuple[str, dict]:
    """
    Normalizes Neon Postgres connection URLs for asyncpg compatibility.
    Neon typically gives:
      postgresql://user:pass@ep-xyz.region.aws.neon.tech/neondb?sslmode=require
    asyncpg requires:
      postgresql+asyncpg://... and ssl='require' in connect_args.
    """
    connect_args = {}
    
    if url.startswith("sqlite"):
        return url, {"check_same_thread": False}

    # Normalize protocol for asyncpg
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Handle sslmode/ssl for Neon
    sslmode = query_params.pop("sslmode", None)
    ssl = query_params.pop("ssl", None)
    
    if sslmode or ssl or "neon.tech" in (parsed.hostname or ""):
        # Neon always enforces SSL/TLS
        connect_args["ssl"] = "require"
    
    # Rebuild URL without sslmode query parameter since asyncpg expects it via connect_args
    clean_query = urlencode(query_params, doseq=True)
    clean_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        clean_query,
        parsed.fragment
    ))

    return clean_url, connect_args


db_url, connect_args = normalize_database_url(settings.DATABASE_URL)

engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
    "connect_args": connect_args,
}

# Only configure connection pooling for PostgreSQL (SQLite doesn't use queue pool)
if not db_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": settings.DB_POOL_PRE_PING,
    })

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an isolated async database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
