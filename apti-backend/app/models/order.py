import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, enum.Enum):
    VIETQR = "VIETQR"
    MOMO = "MOMO"
    VNPAY = "VNPAY"
    BANK_TRANSFER = "BANK_TRANSFER"


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # e.g. APTI-20261028-12345
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(50), ForeignKey("pricing_plans.id"), nullable=False)
    
    amount_vnd: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status_enum", native_enum=False),
        default=OrderStatus.PENDING,
        nullable=False
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method_enum", native_enum=False),
        default=PaymentMethod.VIETQR,
        nullable=False
    )
    transaction_code: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    qr_payment_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    plan: Mapped["PricingPlan"] = relationship("PricingPlan", back_populates="orders")
