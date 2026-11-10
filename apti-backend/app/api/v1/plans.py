from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.base import ensure_utc
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.plan import PricingPlan
from app.schemas.plan import PricingPlanResponse, MySubscriptionResponse
from app.schemas.common import APIResponse

router = APIRouter(prefix="/plans", tags=["Gói học & Đăng ký (Pricing Plans)"])


@router.get("", response_model=APIResponse[List[PricingPlanResponse]])
async def get_pricing_plans(db: AsyncSession = Depends(get_db)):
    """Lấy danh sách các gói luyện thi APTI (Gói 7 Ngày, Gói 30 Ngày Chinh phục MT)."""
    stmt = select(PricingPlan).where(PricingPlan.is_active == True)
    plans = (await db.execute(stmt)).scalars().all()
    return APIResponse(
        data=[PricingPlanResponse.model_validate(p) for p in plans]
    )


@router.get("/my-subscription", response_model=APIResponse[MySubscriptionResponse])
async def get_my_subscription(current_user: User = Depends(get_current_user)):
    """Lấy tình trạng gói bản quyền hiện tại của tài khoản."""
    now = datetime.now(timezone.utc)
    days_left = 0
    expires_at = ensure_utc(current_user.subscription_expires_at)
    if expires_at and expires_at > now:
        days_left = max(0, (expires_at - now).days)

    return APIResponse(
        data=MySubscriptionResponse(
            tier=current_user.subscription_tier,
            has_active_subscription=current_user.has_active_subscription,
            subscription_expires_at=current_user.subscription_expires_at,
            days_remaining=days_left
        )
    )

