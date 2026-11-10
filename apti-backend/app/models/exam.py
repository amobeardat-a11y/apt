from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, Float, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class Exam(Base, TimestampMixin):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # None = Mock Test Tổng hợp
    time_limit_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    passing_score: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    question_ids: Mapped[List[int]] = mapped_column(JSON, default=list, nullable=False)
