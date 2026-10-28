from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user, get_current_user_optional, require_admin
from app.models.user import User
from app.models.quiz import Question
from app.schemas.quiz import (
    CategoryResponse,
    QuestionPublicResponse,
    QuestionDetailResponse,
    QuestionCreate,
    QuestionUpdate,
    QuizSubmitRequest,
    QuizResultResponse,
    QuizAttemptHistoryResponse,
    LeaderboardItem
)
from app.schemas.common import APIResponse
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quiz", tags=["Luyện thi & Đánh giá năng lực (Quiz & Tests)"])


@router.get("/categories", response_model=APIResponse[List[CategoryResponse]])
async def get_quiz_categories(db: AsyncSession = Depends(get_db)):
    """Lấy danh mục các dạng bài thi Aptitude Test (Số học, Logic, Ngôn ngữ, Hình ảnh)."""
    categories = await QuizService.get_categories(db)
    return APIResponse(data=categories)


@router.get("/questions", response_model=APIResponse[List[QuestionPublicResponse]])
async def get_quiz_questions(
    category_id: Optional[str] = Query(None, description="Lọc theo dạng đề: numerical, logical, verbal, abstract"),
    mode: str = Query("PRACTICE", description="PRACTICE hoặc MOCK_EXAM"),
    limit: int = Query(10, ge=1, le=50),
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách câu hỏi để làm bài.
    BẢO MẬT ĐỀ THI: Không chứa đáp án đúng hoặc lời giải trong phản hồi để chống F12 gian lận.
    Người dùng chưa mua gói được giới hạn tối đa 5 câu hỏi mẫu miễn phí.
    """
    questions = await QuizService.get_questions_for_session(
        db, category_id=category_id, mode=mode, limit=limit, user=user
    )
    return APIResponse(data=questions)


@router.post("/submit", response_model=APIResponse[QuizResultResponse])
async def submit_quiz(
    req: QuizSubmitRequest,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Nộp bài thi Aptitude Test.
    Hệ thống chấm điểm trên Server, phân tích tỷ lệ đúng theo từng dạng câu hỏi,
    trả về đáp án chuẩn, lời giải chi tiết bằng tiếng Việt và lời nhắn khích lệ từ Linh vật Em Tee.
    Nếu người dùng đã đăng nhập, kết quả sẽ được lưu vào lịch sử tiến độ.
    """
    result = await QuizService.grade_quiz_submission(db, req, user=user)
    return APIResponse(
        message="Chấm điểm bài thi hoàn tất!",
        data=result
    )


@router.get("/history", response_model=APIResponse[List[QuizAttemptHistoryResponse]])
async def get_my_quiz_history(
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Lấy lịch sử các lần giải đề và tiến bộ điểm số của người dùng hiện tại."""
    history = await QuizService.get_user_history(db, current_user.id, limit=limit)
    return APIResponse(
        data=[QuizAttemptHistoryResponse.model_validate(h) for h in history]
    )


@router.get("/leaderboard", response_model=APIResponse[List[LeaderboardItem]])
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Bảng xếp hạng Top các học viên có điểm số xuất sắc nhất trên APTI."""
    board = await QuizService.get_leaderboard(db, limit=limit)
    return APIResponse(data=board)


# ================= ADMIN QUESTION MANAGEMENT =================

@router.post("/admin/questions", response_model=APIResponse[QuestionDetailResponse], status_code=status.HTTP_201_CREATED)
async def create_question_admin(
    req: QuestionCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Thêm câu hỏi trắc nghiệm mới vào ngân hàng đề."""
    new_q = Question(
        category_id=req.category_id,
        level=req.level,
        question_text=req.question_text,
        options=req.options,
        correct_index=req.correct_index,
        explanation=req.explanation,
        tip=req.tip,
        is_premium=req.is_premium,
        time_limit_seconds=req.time_limit_seconds,
        is_active=True
    )
    db.add(new_q)
    await db.commit()
    await db.refresh(new_q)
    return APIResponse(
        message="Thêm câu hỏi thành công",
        data=QuestionDetailResponse.model_validate(new_q)
    )


@router.put("/admin/questions/{question_id}", response_model=APIResponse[QuestionDetailResponse])
async def update_question_admin(
    question_id: int,
    req: QuestionUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Cập nhật nội dung câu hỏi trong ngân hàng đề."""
    q = await db.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(q, key, value)

    await db.commit()
    await db.refresh(q)
    return APIResponse(
        message="Cập nhật câu hỏi thành công",
        data=QuestionDetailResponse.model_validate(q)
    )


@router.delete("/admin/questions/{question_id}", response_model=APIResponse[None])
async def delete_question_admin(
    question_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Vô hiệu hóa hoặc xóa câu hỏi."""
    q = await db.get(Question, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")

    q.is_active = False
    await db.commit()
    return APIResponse(message="Đã gỡ bỏ câu hỏi khỏi ngân hàng đề.")

