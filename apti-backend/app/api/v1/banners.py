from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.banner import Banner
from app.schemas.admin_entities import BannerResponse
from app.schemas.common import APIResponse

router = APIRouter(prefix="/banners", tags=["Banner quảng bá & sự kiện (Banners)"])


@router.get("", response_model=APIResponse[List[BannerResponse]])
async def list_public_banners(db: AsyncSession = Depends(get_db)):
    """Lấy danh sách các banner quảng bá đang kích hoạt."""
    stmt = select(Banner).where(Banner.is_active == True).order_by(Banner.display_order.asc())
    banners = (await db.execute(stmt)).scalars().all()
    return APIResponse(data=[BannerResponse.model_validate(b) for b in banners])
