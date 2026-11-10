from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.exam import Exam
from app.models.quiz import Question
from app.schemas.admin_entities import ExamResponse, ExamDetailResponse
from app.schemas.quiz import QuestionPublicResponse, QuizSubmitRequest, QuizResultResponse, QuestionReviewItem
from app.schemas.common import APIResponse

router = APIRouter(prefix="/exams", tags=["Đề thi thử (Mock Exams)"])


@router.get("", response_model=APIResponse[List[ExamResponse]])
async def list_public_exams(
    category_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách các đề thi thử năng lực đang kích hoạt."""
    stmt = select(Exam).where(Exam.is_active == True)
    if category_id:
        stmt = stmt.where(Exam.category_id == category_id)

    exams = (await db.execute(stmt)).scalars().all()
    results = []
    for e in exams:
        item = ExamResponse(
            id=e.id,
            title=e.title,
            description=e.description,
            category_id=e.category_id,
            time_limit_minutes=e.time_limit_minutes,
            passing_score=e.passing_score,
            is_premium=e.is_premium,
            is_active=e.is_active,
            questions_count=len(e.question_ids),
            question_ids=e.question_ids
        )
        results.append(item)

    return APIResponse(data=results)


@router.get("/{exam_id}", response_model=APIResponse[ExamDetailResponse])
async def get_exam_for_test(
    exam_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy đề thi để bắt đầu làm bài:
    BẢO MẬT ANTI-CHEAT: Toàn bộ đáp án đúng (correct_index) và lời giải (explanation)
    bị loại bỏ hoàn toàn khỏi phản hồi HTTP để tránh học viên mở F12 xem trước đáp án!
    """
    exam = await db.get(Exam, exam_id)
    if not exam or not exam.is_active:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi hoặc đề thi chưa được kích hoạt.")

    # Fetch questions
    questions_list = []
    if exam.question_ids:
        stmt = select(Question).where(Question.id.in_(exam.question_ids), Question.is_active == True)
        raw_questions = (await db.execute(stmt)).scalars().all()
        # Maintain order of exam.question_ids
        q_map = {q.id: q for q in raw_questions}
        for qid in exam.question_ids:
            if qid in q_map:
                q = q_map[qid]
                questions_list.append(QuestionPublicResponse(
                    id=q.id,
                    category_id=q.category_id,
                    level=q.level,
                    question_text=q.question_text,
                    options=q.options,
                    time_limit_seconds=q.time_limit_seconds
                ))

    detail = ExamDetailResponse(
        id=exam.id,
        title=exam.title,
        description=exam.description,
        category_id=exam.category_id,
        time_limit_minutes=exam.time_limit_minutes,
        passing_score=exam.passing_score,
        is_premium=exam.is_premium,
        is_active=exam.is_active,
        questions_count=len(questions_list),
        question_ids=exam.question_ids,
        questions=questions_list
    )

    return APIResponse(data=detail)


@router.post("/{exam_id}/submit", response_model=APIResponse[QuizResultResponse])
async def submit_exam_and_grade(
    exam_id: int,
    req: QuizSubmitRequest,
    db: AsyncSession = Depends(get_db)
):
    """Chấm điểm đề thi thử trên máy chủ và trả về phân tích chi tiết từng câu."""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Đề thi không tồn tại.")

    user_answers_map = {a.question_id: a.selected_index for a in req.answers}
    question_ids = list(user_answers_map.keys())

    if not question_ids:
        return APIResponse(
            data=QuizResultResponse(
                total_questions=0,
                correct_answers=0,
                score_percentage=0.0,
                time_spent_seconds=req.time_spent_seconds,
                category_breakdown={},
                reviews=[],
                mascot_message="Bạn chưa trả lời câu hỏi nào!"
            )
        )

    stmt = select(Question).where(Question.id.in_(question_ids))
    questions = (await db.execute(stmt)).scalars().all()

    correct_count = 0
    detailed_review = []
    category_stats = {}

    for q in questions:
        selected_idx = user_answers_map.get(q.id, -1)
        is_correct = (selected_idx == q.correct_index)
        if is_correct:
            correct_count += 1

        cat = q.category_id
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "correct": 0}
        category_stats[cat]["total"] += 1
        if is_correct:
            category_stats[cat]["correct"] += 1

        detailed_review.append(QuestionReviewItem(
            question_id=q.id,
            question_text=q.question_text,
            category_id=q.category_id,
            options=q.options,
            selected_index=selected_idx,
            correct_index=q.correct_index,
            is_correct=is_correct,
            explanation=q.explanation,
            tip=q.tip
        ))

    total = len(questions)
    percentage = round((correct_count / total * 100), 1) if total > 0 else 0.0

    passed = percentage >= exam.passing_score
    if percentage >= 90:
        feedback = f"🌟 Xuất sắc! Bạn đạt {percentage}% ({correct_count}/{total} câu). Bạn đã sẵn sàng vượt qua vòng test thật của các tập đoàn lớn!"
    elif passed:
        feedback = f"🎉 Chúc mừng! Bạn đạt {percentage}%, vượt qua điểm chuẩn {exam.passing_score}% của đề thi này!"
    else:
        feedback = f"💪 Bạn đạt {percentage}%. Điểm chuẩn là {exam.passing_score}%. Đừng nản lòng, hãy xem lại lời giải chi tiết và thử lại nhé!"

    return APIResponse(
        message="Chấm điểm đề thi thành công",
        data=QuizResultResponse(
            total_questions=total,
            correct_answers=correct_count,
            score_percentage=percentage,
            time_spent_seconds=req.time_spent_seconds,
            category_breakdown=category_stats,
            reviews=detailed_review,
            mascot_message=feedback
        )
    )
