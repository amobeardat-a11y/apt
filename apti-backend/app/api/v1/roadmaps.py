from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.roadmap import Roadmap
from app.schemas.admin_entities import RoadmapResponse
from app.schemas.common import APIResponse

router = APIRouter(prefix="/roadmaps", tags=["Lộ trình học tập (Roadmaps)"])


@router.get("", response_model=APIResponse[List[RoadmapResponse]])
async def list_public_roadmaps(db: AsyncSession = Depends(get_db)):
    """Lấy danh sách các lộ trình học tập đang kích hoạt."""
    stmt = select(Roadmap).where(Roadmap.is_active == True).order_by(Roadmap.display_order.asc())
    roadmaps = (await db.execute(stmt)).scalars().all()
    return APIResponse(data=[RoadmapResponse.model_validate(r) for r in roadmaps])
