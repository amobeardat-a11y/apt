from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quiz import Category, Question, QuizAttempt
from app.models.user import User, SubscriptionTier
from app.schemas.quiz import (
    CategoryResponse,
    QuestionPublicResponse,
    QuizSubmitRequest,
    QuizResultResponse,
    QuestionReviewItem,
    LeaderboardItem
)


class QuizService:

    @staticmethod
    async def get_categories(db: AsyncSession) -> List[CategoryResponse]:
        # Count questions per category
        count_subquery = (
            select(Question.category_id, func.count(Question.id).label("q_count"))
            .where(Question.is_active == True)
            .group_by(Question.category_id)
            .subquery()
        )

        stmt = (
            select(
                Category,
                func.coalesce(count_subquery.c.q_count, 0).label("question_count")
            )
            .outerjoin(count_subquery, Category.id == count_subquery.c.category_id)
            .order_by(Category.display_order.asc())
        )
        results = (await db.execute(stmt)).all()

        categories = []
        for cat, q_count in results:
            categories.append(CategoryResponse(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                icon=cat.icon,
                display_order=cat.display_order,
                question_count=int(q_count)
            ))
        return categories

    @staticmethod
    async def get_questions_for_session(
        db: AsyncSession,
        category_id: Optional[str] = None,
        mode: str = "PRACTICE",
        limit: int = 10,
        user: Optional[User] = None
    ) -> List[QuestionPublicResponse]:
        """
        Retrieves randomized or curated questions.
        Censors correct_index and explanation to uphold test integrity.
        Free / Anonymous users get capped to free sample questions.
        """
        has_full_access = (
            user is not None and 
            (user.has_active_subscription or user.role.value == "ADMIN")
        )

        stmt = select(Question).where(Question.is_active == True)
        if category_id and category_id != "all":
            stmt = stmt.where(Question.category_id == category_id)

        if not has_full_access:
            # Free tier only accesses non-premium questions, max 5 questions per practice
            stmt = stmt.where(Question.is_premium == False)
            limit = min(limit, 5)
        else:
            limit = min(limit, 50)

        stmt = stmt.order_by(func.random()).limit(limit)
        questions = (await db.execute(stmt)).scalars().all()

        return [
            QuestionPublicResponse(
                id=q.id,
                category_id=q.category_id,
                level=q.level,
                question_text=q.question_text,
                options=q.options,
                time_limit_seconds=q.time_limit_seconds
            )
            for q in questions
        ]

    @staticmethod
    async def grade_quiz_submission(
        db: AsyncSession,
        req: QuizSubmitRequest,
        user: Optional[User] = None
    ) -> QuizResultResponse:
        """Grades the quiz, calculates score, generates feedback & optionally persists attempt."""
        question_ids = [a.question_id for a in req.answers]
        if not question_ids:
            return QuizResultResponse(
                total_questions=0,
                correct_answers=0,
                score_percentage=0.0,
                time_spent_seconds=req.time_spent_seconds,
                category_breakdown={},
                reviews=[],
                mascot_message="Bạn chưa trả lời câu hỏi nào. Hãy thử lại cùng Em Tee nhé!"
            )

        # Fetch questions from DB
        stmt = select(Question).where(Question.id.in_(question_ids))
        questions = (await db.execute(stmt)).scalars().all()
        q_map = {q.id: q for q in questions}

        total_questions = len(req.answers)
        correct_count = 0
        reviews: List[QuestionReviewItem] = []
        cat_stats: Dict[str, Dict[str, int]] = {}

        for ans in req.answers:
            q = q_map.get(ans.question_id)
            if not q:
                continue

            is_correct = (ans.selected_index == q.correct_index)
            if is_correct:
                correct_count += 1

            # Stats per category
            cat_id = q.category_id
            if cat_id not in cat_stats:
                cat_stats[cat_id] = {"total": 0, "correct": 0}
            cat_stats[cat_id]["total"] += 1
            if is_correct:
                cat_stats[cat_id]["correct"] += 1

            reviews.append(QuestionReviewItem(
                question_id=q.id,
                question_text=q.question_text,
                category_id=q.category_id,
                options=q.options,
                selected_index=ans.selected_index,
                correct_index=q.correct_index,
                is_correct=is_correct,
                explanation=q.explanation,
                tip=q.tip
            ))

        score_percentage = round((correct_count / total_questions) * 100, 1) if total_questions > 0 else 0.0

        # Formulate category breakdown with percentage
        category_breakdown = {}
        for cat_id, stats in cat_stats.items():
            pct = round((stats["correct"] / stats["total"]) * 100, 1) if stats["total"] > 0 else 0.0
            category_breakdown[cat_id] = {
                "total": stats["total"],
                "correct": stats["correct"],
                "percentage": pct
            }

        # Em Tee Mascot Motivational Message
        if score_percentage >= 90:
            mascot_msg = "Xuất sắc! Bạn có tư duy logic sắc bén chuẩn Management Trainee! Tiếp tục giữ vững phong độ nhé!"
        elif score_percentage >= 70:
            mascot_msg = "Làm rất tốt! Bạn đã nắm chắc hầu hết các bẫy đề thi. Xem thêm mẹo giải nhanh để tối ưu thời gian nha!"
        elif score_percentage >= 50:
            mascot_msg = "Khởi đầu ấn tượng! Đừng lo lắng, hãy xem kỹ lời giải chi tiết của Em Tee ở từng câu để rút kinh nghiệm nhé!"
        else:
            mascot_msg = "Bắt đầu từ con số 0 cũng chẳng sao! Mỗi câu làm được là một bước tiến rồi. Hãy luyện tập đều đặn cùng APTI nha!"

        attempt_id = None
        # If user is authenticated, persist attempt in Neon Postgres
        if user:
            attempt = QuizAttempt(
                user_id=user.id,
                category_id=req.category_id,
                mode=req.mode,
                total_questions=total_questions,
                correct_answers=correct_count,
                score_percentage=score_percentage,
                time_spent_seconds=req.time_spent_seconds,
                completed=True,
                completed_at=datetime.now(timezone.utc),
                answer_details=[
                    {
                        "question_id": r.question_id,
                        "selected_index": r.selected_index,
                        "correct_index": r.correct_index,
                        "is_correct": r.is_correct
                    }
                    for r in reviews
                ]
            )
            db.add(attempt)
            await db.commit()
            await db.refresh(attempt)
            attempt_id = attempt.id

        return QuizResultResponse(
            attempt_id=attempt_id,
            total_questions=total_questions,
            correct_answers=correct_count,
            score_percentage=score_percentage,
            time_spent_seconds=req.time_spent_seconds,
            category_breakdown=category_breakdown,
            reviews=reviews,
            mascot_message=mascot_msg
        )

    @staticmethod
    async def get_user_history(db: AsyncSession, user_id: int, limit: int = 20) -> List[QuizAttempt]:
        stmt = (
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .order_by(desc(QuizAttempt.created_at))
            .limit(limit)
        )
        return list((await db.execute(stmt)).scalars().all())

    @staticmethod
    async def get_leaderboard(db: AsyncSession, limit: int = 10) -> List[LeaderboardItem]:
        stmt = (
            select(
                User.full_name,
                func.count(QuizAttempt.id).label("total_attempts"),
                func.avg(QuizAttempt.score_percentage).label("avg_score"),
                func.max(QuizAttempt.score_percentage).label("max_score")
            )
            .join(QuizAttempt, User.id == QuizAttempt.user_id)
            .where(QuizAttempt.completed == True)
            .group_by(User.id)
            .order_by(desc("max_score"), desc("avg_score"))
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()

        leaderboard = []
        for idx, (name, total, avg_s, max_s) in enumerate(rows, 1):
            leaderboard.append(LeaderboardItem(
                rank=idx,
                user_name=name,
                total_attempts=int(total),
                average_score=round(float(avg_s), 1),
                highest_score=round(float(max_s), 1)
            ))
        return leaderboard

