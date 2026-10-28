import time
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.config import settings
from app.schemas.common import APIResponse

router = APIRouter(tags=["Giám sát hệ thống (Health Check)"])

START_TIME = time.time()


@router.get("/health", response_model=APIResponse[dict])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint:
    Pings Neon PostgreSQL database to ensure connectivity,
    returns uptime and system status.
    """
    db_status = "HEALTHY"
    db_latency_ms = 0.0
    try:
        t0 = time.perf_counter()
        await db.execute(text("SELECT 1"))
        db_latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    except Exception as exc:
        db_status = f"UNHEALTHY: {str(exc)}"

    uptime_seconds = int(time.time() - START_TIME)

    return APIResponse(
        message="Hệ thống APTI Backend hoạt động bình thường",
        data={
            "status": "UP" if db_status == "HEALTHY" else "DEGRADED",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "uptime_seconds": uptime_seconds,
            "database": {
                "status": db_status,
                "latency_ms": db_latency_ms,
                "target": "Neon PostgreSQL Serverless"
            }
        }
    )

