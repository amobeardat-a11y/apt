from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.user import SubscriptionTier


class PricingPlanResponse(BaseModel):
    id: str
    name: str
    tagline: str
    price_vnd: int
    original_price_vnd: int
    duration_days: int
    badge: Optional[str] = None
    popular: bool
    is_active: bool
    features: List[str]

    model_config = ConfigDict(from_attributes=True)


class MySubscriptionResponse(BaseModel):
    tier: SubscriptionTier
    has_active_subscription: bool
    subscription_expires_at: Optional[datetime] = None
    days_remaining: int = 0

