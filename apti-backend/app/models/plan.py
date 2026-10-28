from typing import List, Optional
from sqlalchemy import String, Boolean, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class PricingPlan(Base, TimestampMixin):
    __tablename__ = "pricing_plans"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # 'starter-7d', 'master-30d'
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tagline: Mapped[str] = mapped_column(String(255), nullable=False)
    price_vnd: Mapped[int] = mapped_column(Integer, nullable=False)  # 99000, 249000
    original_price_vnd: Mapped[int] = mapped_column(Integer, nullable=False)  # 149000, 399000
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)  # 7, 30
    badge: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'Khởi động', 'Được chọn nhiều nhất'
    popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    features: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="plan")
