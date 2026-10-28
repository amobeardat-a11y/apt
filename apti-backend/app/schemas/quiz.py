from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: int
    question_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class QuestionPublicResponse(BaseModel):
    """
    Public Question Schema for Exam/Practice mode:
    CRITICAL SECURITY & INTEGRITY: Does NOT include correct_index or explanation
    so clients cannot inspect HTTP responses to cheat!
    """
    id: int
    category_id: str
    level: str
    question_text: str
    options: List[str]
    time_limit_seconds: int

    model_config = ConfigDict(from_attributes=True)


class QuestionDetailResponse(QuestionPublicResponse):
    """Full Question Schema returned after submission or to Admin/Instructors."""
    correct_index: int
    explanation: str
    tip: Optional[str] = None
    is_premium: bool
    is_active: bool


class QuestionCreate(BaseModel):
    category_id: str
    level: str = "Cơ bản"
    question_text: str
    options: List[str]
    correct_index: int
    explanation: str
    tip: Optional[str] = None
    is_premium: bool = False
    time_limit_seconds: int = 90


class QuestionUpdate(BaseModel):
    category_id: Optional[str] = None
    level: Optional[str] = None
    question_text: Optional[str] = None
    options: Optional[List[str]] = None
    correct_index: Optional[int] = None
    explanation: Optional[str] = None
    tip: Optional[str] = None
    is_premium: Optional[bool] = None
    time_limit_seconds: Optional[int] = None
    is_active: Optional[bool] = None


class QuizStartRequest(BaseModel):
    category_id: Optional[str] = None
    mode: str = "PRACTICE"  # 'PRACTICE', 'MOCK_EXAM'
    limit: int = 10


class AnswerItem(BaseModel):
    question_id: int
    selected_index: int  # 0, 1, 2, 3 or -1 if skipped


class QuizSubmitRequest(BaseModel):
    category_id: Optional[str] = None
    mode: str = "PRACTICE"
    time_spent_seconds: int
    answers: List[AnswerItem]


class QuestionReviewItem(BaseModel):
    question_id: int
    question_text: str
    category_id: str
    options: List[str]
    selected_index: int
    correct_index: int
    is_correct: bool
    explanation: str
    tip: Optional[str] = None


class QuizResultResponse(BaseModel):
    attempt_id: Optional[int] = None
    total_questions: int
    correct_answers: int
    score_percentage: float
    time_spent_seconds: int
    category_breakdown: Dict[str, Dict[str, Any]]
    reviews: List[QuestionReviewItem]
    mascot_message: str


class QuizAttemptHistoryResponse(BaseModel):
    id: int
    category_id: Optional[str] = None
    mode: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    time_spent_seconds: int
    completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaderboardItem(BaseModel):
    rank: int
    user_name: str
    total_attempts: int
    average_score: float
    highest_score: float

