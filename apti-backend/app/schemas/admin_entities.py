from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.quiz import QuestionPublicResponse


# --- Exam Schemas ---
class ExamResponse(BaseModel):
    id: int
    title: str
    description: str
    category_id: Optional[str] = None
    time_limit_minutes: int
    passing_score: float
    is_premium: bool
    is_active: bool
    questions_count: int = 0
    question_ids: List[int] = []

    model_config = ConfigDict(from_attributes=True)


class ExamDetailResponse(ExamResponse):
    questions: List[QuestionPublicResponse] = []


class ExamCreate(BaseModel):
    title: str
    description: str
    category_id: Optional[str] = None
    time_limit_minutes: int = 30
    passing_score: float = 70.0
    is_premium: bool = False
    is_active: bool = True
    question_ids: Optional[List[int]] = None
    random_count: Optional[int] = None  # If provided, randomly pick N questions


class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    passing_score: Optional[float] = None
    is_premium: Optional[bool] = None
    is_active: Optional[bool] = None
    question_ids: Optional[List[int]] = None


# --- Roadmap Schemas ---
class RoadmapPhase(BaseModel):
    week: int
    title: str
    description: str
    targets: List[str] = []
    recommended_topics: List[str] = []


class RoadmapResponse(BaseModel):
    id: str
    title: str
    subtitle: str
    target_role: str
    duration_weeks: int
    phases: List[Dict[str, Any]]
    is_active: bool
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class RoadmapCreate(BaseModel):
    id: str
    title: str
    subtitle: str
    target_role: str = "Management Trainee"
    duration_weeks: int = 4
    phases: List[Dict[str, Any]] = []
    is_active: bool = True
    display_order: int = 0


class RoadmapUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    target_role: Optional[str] = None
    duration_weeks: Optional[int] = None
    phases: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


# --- Banner Schemas ---
class BannerResponse(BaseModel):
    id: int
    title: str
    badge_text: str
    description: str
    cta_text: str
    link_url: str
    image_url: Optional[str] = None
    bg_gradient: str
    is_active: bool
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class BannerCreate(BaseModel):
    title: str
    badge_text: str = "HOT"
    description: str
    cta_text: str = "Khám phá ngay"
    link_url: str = "#"
    image_url: Optional[str] = None
    bg_gradient: str = "linear-gradient(135deg, #5348CD, #F54899)"
    is_active: bool = True
    display_order: int = 0


class BannerUpdate(BaseModel):
    title: Optional[str] = None
    badge_text: Optional[str] = None
    description: Optional[str] = None
    cta_text: Optional[str] = None
    link_url: Optional[str] = None
    image_url: Optional[str] = None
    bg_gradient: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

