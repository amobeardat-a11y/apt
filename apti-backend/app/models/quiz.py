from datetime import datetime, timezone
from typing import Optional, List, Any
from sqlalchemy import String, Boolean, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # 'numerical', 'logical', 'verbal', 'abstract'
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    questions: Mapped[List["Question"]] = relationship("Question", back_populates="category")


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_id: Mapped[str] = mapped_column(String(50), ForeignKey("categories.id"), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(50), default="Cơ bản", nullable=False)  # 'Cơ bản', 'Thực tế', 'Suy luận', 'Nâng cao'
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[List[str]] = mapped_column(JSON, nullable=False)  # List of 4 string options
    correct_index: Mapped[int] = mapped_column(Integer, nullable=False)  # 0, 1, 2, 3
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    tip: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="questions")


class QuizAttempt(Base, TimestampMixin):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mode: Mapped[str] = mapped_column(String(50), default="PRACTICE", nullable=False)  # 'PRACTICE', 'MOCK_EXAM', 'CHALLENGE'
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Stored answers snapshot: list of dicts [{question_id, selected_index, is_correct}]
    answer_details: Mapped[List[dict]] = mapped_column(JSON, default=list, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="quiz_attempts")
