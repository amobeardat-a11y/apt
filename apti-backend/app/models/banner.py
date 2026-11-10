from typing import Optional
from sqlalchemy import String, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class Banner(Base, TimestampMixin):
    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    badge_text: Mapped[str] = mapped_column(String(50), default="HOT", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cta_text: Mapped[str] = mapped_column(String(50), default="Khám phá ngay", nullable=False)
    link_url: Mapped[str] = mapped_column(String(255), default="#", nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bg_gradient: Mapped[str] = mapped_column(
        String(255),
        default="linear-gradient(135deg, #5348CD, #F54899)",
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

