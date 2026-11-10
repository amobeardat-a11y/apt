from typing import List, Dict, Any
from sqlalchemy import String, Boolean, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class Roadmap(Base, TimestampMixin):
    __tablename__ = "roadmaps"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., 'mt-fasttrack-4w'
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(255), nullable=False)
    target_role: Mapped[str] = mapped_column(String(100), default="Management Trainee", nullable=False)
    duration_weeks: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    phases: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
