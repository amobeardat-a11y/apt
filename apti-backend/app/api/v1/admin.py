from datetime import datetime, timedelta, timezone
from typing import List, Optional
import random
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.base import ensure_utc
from app.core.dependencies import require_admin
from app.models.user import User, SubscriptionTier, UserRole
from app.models.quiz import QuizAttempt, Question, Category
from app.models.order import Order, OrderStatus
from app.models.exam import Exam
from app.models.roadmap import Roadmap
from app.models.banner import Banner

from app.schemas.user import UserResponse, UserAdminUpdate
from app.schemas.quiz import QuestionCreate, QuestionUpdate, QuestionDetailResponse
from app.schemas.admin_entities import (
    ExamResponse, ExamCreate, ExamUpdate,
    RoadmapResponse, RoadmapCreate, RoadmapUpdate,
    BannerResponse, BannerCreate, BannerUpdate
)
from app.schemas.common import APIResponse, PaginatedResponse

router = APIRouter(prefix="/admin", tags=["Quản trị hệ thống (Admin Dashboard)"])


# =========================================================================
# 1. ADMIN STATS & USERS
# =========================================================================

@router.get("/stats", response_model=APIResponse[dict])
async def get_admin_dashboard_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Lấy tổng quan số liệu thống kê thời gian thực của nền tảng APTI."""
    now = datetime.now(timezone.utc)

    # Total users
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one() or 0

    # Active paid subscribers
    active_subs_stmt = select(func.count(User.id)).where(
        User.subscription_tier != SubscriptionTier.FREE,
        User.subscription_expires_at > now
    )
    active_subscribers = (await db.execute(active_subs_stmt)).scalar_one() or 0

    # Total revenue in VND
    revenue_stmt = select(func.sum(Order.amount_vnd)).where(Order.status == OrderStatus.COMPLETED)
    total_revenue = (await db.execute(revenue_stmt)).scalar_one() or 0

    # Total completed quizzes
    quiz_stmt = select(func.count(QuizAttempt.id)).where(QuizAttempt.completed == True)
    total_quizzes = (await db.execute(quiz_stmt)).scalar_one() or 0

    # Average quiz score
    avg_score_stmt = select(func.avg(QuizAttempt.score_percentage)).where(QuizAttempt.completed == True)
    avg_score = (await db.execute(avg_score_stmt)).scalar_one() or 0.0

    # Total questions in bank
    total_questions = (await db.execute(select(func.count(Question.id)).where(Question.is_active == True))).scalar_one() or 0

    # Total exams
    total_exams = (await db.execute(select(func.count(Exam.id)).where(Exam.is_active == True))).scalar_one() or 0

    # Total roadmaps
    total_roadmaps = (await db.execute(select(func.count(Roadmap.id)).where(Roadmap.is_active == True))).scalar_one() or 0

    # Total banners
    total_banners = (await db.execute(select(func.count(Banner.id)).where(Banner.is_active == True))).scalar_one() or 0

    return APIResponse(
        data={
            "total_users": total_users,
            "active_subscribers": active_subscribers,
            "total_revenue_vnd": int(total_revenue),
            "total_quizzes_taken": total_quizzes,
            "average_quiz_score": round(float(avg_score), 1),
            "total_questions_bank": total_questions,
            "total_exams": total_exams,
            "total_roadmaps": total_roadmaps,
            "total_banners": total_banners,
            "system_health": "OPTIMAL",
            "database_provider": "Neon PostgreSQL Serverless"
        }
    )


@router.get("/users", response_model=APIResponse[PaginatedResponse[UserResponse]])
async def list_users_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Quản lý danh sách học viên, tìm kiếm và phân trang."""
    stmt = select(User)
    if search:
        s = f"%{search.strip().lower()}%"
        stmt = stmt.where((User.email.ilike(s)) | (User.full_name.ilike(s)))
    if role:
        stmt = stmt.where(User.role == role)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one() or 0

    stmt = stmt.order_by(desc(User.created_at)).offset((page - 1) * page_size).limit(page_size)
    users = (await db.execute(stmt)).scalars().all()

    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

    return APIResponse(
        data=PaginatedResponse(
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.put("/users/{user_id}", response_model=APIResponse[UserResponse])
async def update_user_status_admin(
    user_id: int,
    req: UserAdminUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Cập nhật quyền hạn, kích hoạt/vô hiệu hóa, hoặc cộng thêm ngày sử dụng gói học."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

    if req.role is not None:
        user.role = req.role
    if req.is_active is not None:
        user.is_active = req.is_active
    if req.subscription_tier is not None:
        user.subscription_tier = req.subscription_tier
    if req.subscription_days_to_add:
        now = datetime.now(timezone.utc)
        current_exp = ensure_utc(user.subscription_expires_at)
        start = current_exp if (current_exp and current_exp > now) else now
        user.subscription_expires_at = start + timedelta(days=req.subscription_days_to_add)

    await db.commit()
    await db.refresh(user)
    return APIResponse(
        message="Cập nhật thông tin học viên thành công",
        data=UserResponse.model_validate(user)
    )


# =========================================================================
# 2. ADMIN QUESTION BANK MANAGEMENT (NGÂN HÀNG CÂU HỎI 1000+)
# =========================================================================

@router.get("/questions", response_model=APIResponse[PaginatedResponse[QuestionDetailResponse]])
async def list_questions_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Xem danh sách toàn bộ câu hỏi trong ngân hàng, lọc và tìm kiếm."""
    stmt = select(Question)
    if category_id:
        stmt = stmt.where(Question.category_id == category_id)
    if level:
        stmt = stmt.where(Question.level == level)
    if search:
        s = f"%{search.strip().lower()}%"
        stmt = stmt.where(Question.question_text.ilike(s) | Question.explanation.ilike(s))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one() or 0

    stmt = stmt.order_by(Question.id.asc()).offset((page - 1) * page_size).limit(page_size)
    questions = (await db.execute(stmt)).scalars().all()

    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

    return APIResponse(
        data=PaginatedResponse(
            items=[
                QuestionDetailResponse(
                    id=q.id,
                    category_id=q.category_id,
                    level=q.level,
                    question_text=q.question_text,
                    options=q.options,
                    time_limit_seconds=q.time_limit_seconds,
                    correct_index=q.correct_index,
                    explanation=q.explanation,
                    tip=q.tip,
                    is_premium=q.is_premium,
                    is_active=q.is_active
                )
                for q in questions
            ],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.post("/questions", response_model=APIResponse[QuestionDetailResponse], status_code=status.HTTP_201_CREATED)
async def create_question_admin(
    req: QuestionCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Thêm câu hỏi mới vào ngân hàng câu hỏi."""
    # Validate category exists
    cat = await db.get(Category, req.category_id)
    if not cat:
        raise HTTPException(status_code=400, detail=f"Danh mục '{req.category_id}' không tồn tại.")

    # Validate options & correct_index
    if len(req.options) < 2 or len(req.options) > 6:
        raise HTTPException(status_code=400, detail="Số lượng phương án lựa chọn phải từ 2 đến 6.")
    if req.correct_index < 0 or req.correct_index >= len(req.options):
        raise HTTPException(status_code=400, detail="Chỉ số đáp án đúng (correct_index) không hợp lệ.")

    # Get max ID + 1
    max_id = (await db.execute(select(func.max(Question.id)))).scalar_one() or 0
    new_id = max_id + 1

    question = Question(
        id=new_id,
        category_id=req.category_id,
        level=req.level,
        question_text=req.question_text.strip(),
        options=req.options,
        correct_index=req.correct_index,
        explanation=req.explanation.strip(),
        tip=req.tip.strip() if req.tip else None,
        is_premium=req.is_premium,
        time_limit_seconds=req.time_limit_seconds,
        is_active=True
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)

    return APIResponse(
        message="Thêm câu hỏi mới thành công",
        data=QuestionDetailResponse(
            id=question.id,
            category_id=question.category_id,
            level=question.level,
            question_text=question.question_text,
            options=question.options,
            time_limit_seconds=question.time_limit_seconds,
            correct_index=question.correct_index,
            explanation=question.explanation,
            tip=question.tip,
            is_premium=question.is_premium,
            is_active=question.is_active
        )
    )


@router.put("/questions/{question_id}", response_model=APIResponse[QuestionDetailResponse])
async def update_question_admin(
    question_id: int,
    req: QuestionUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Cập nhật nội dung câu hỏi trong ngân hàng."""
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")

    if req.category_id is not None:
        cat = await db.get(Category, req.category_id)
        if not cat:
            raise HTTPException(status_code=400, detail="Danh mục không tồn tại.")
        question.category_id = req.category_id

    if req.level is not None:
        question.level = req.level
    if req.question_text is not None:
        question.question_text = req.question_text.strip()
    if req.options is not None:
        question.options = req.options
    if req.correct_index is not None:
        if req.correct_index < 0 or req.correct_index >= len(question.options):
            raise HTTPException(status_code=400, detail="Chỉ số đáp án đúng không hợp lệ.")
        question.correct_index = req.correct_index
    if req.explanation is not None:
        question.explanation = req.explanation.strip()
    if req.tip is not None:
        question.tip = req.tip.strip() if req.tip else None
    if req.is_premium is not None:
        question.is_premium = req.is_premium
    if req.time_limit_seconds is not None:
        question.time_limit_seconds = req.time_limit_seconds
    if req.is_active is not None:
        question.is_active = req.is_active

    await db.commit()
    await db.refresh(question)

    return APIResponse(
        message="Cập nhật câu hỏi thành công",
        data=QuestionDetailResponse(
            id=question.id,
            category_id=question.category_id,
            level=question.level,
            question_text=question.question_text,
            options=question.options,
            time_limit_seconds=question.time_limit_seconds,
            correct_index=question.correct_index,
            explanation=question.explanation,
            tip=question.tip,
            is_premium=question.is_premium,
            is_active=question.is_active
        )
    )


@router.delete("/questions/{question_id}", response_model=APIResponse[dict])
async def delete_question_admin(
    question_id: int,
    hard_delete: bool = Query(False),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Xóa câu hỏi (mặc định soft-delete đặt is_active=False)."""
    question = await db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")

    if hard_delete:
        await db.delete(question)
    else:
        question.is_active = False

    await db.commit()
    return APIResponse(message=f"Đã {'xóa hoàn toàn' if hard_delete else 'vô hiệu hóa'} câu hỏi #{question_id}")


# =========================================================================
# 3. ADMIN EXAM MANAGEMENT (QUẢN LÝ ĐỀ THI THỬ MOCK EXAMS)
# =========================================================================

@router.get("/exams", response_model=APIResponse[List[ExamResponse]])
async def list_exams_admin(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Danh sách toàn bộ đề thi thử."""
    stmt = select(Exam).order_by(Exam.id.desc())
    exams = (await db.execute(stmt)).scalars().all()
    results = [
        ExamResponse(
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
        for e in exams
    ]
    return APIResponse(data=results)


@router.post("/exams", response_model=APIResponse[ExamResponse], status_code=status.HTTP_201_CREATED)
async def create_exam_admin(
    req: ExamCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Tạo đề thi mới (có hỗ trợ tự động bốc ngẫu nhiên N câu hỏi từ ngân hàng)."""
    question_ids = req.question_ids or []
    if not question_ids and req.random_count and req.random_count > 0:
        q_stmt = select(Question.id).where(Question.is_active == True)
        if req.category_id:
            q_stmt = q_stmt.where(Question.category_id == req.category_id)
        all_ids = (await db.execute(q_stmt)).scalars().all()
        if all_ids:
            sample_size = min(req.random_count, len(all_ids))
            question_ids = random.sample(all_ids, sample_size)

    max_id = (await db.execute(select(func.max(Exam.id)))).scalar_one() or 0
    new_id = max_id + 1

    exam = Exam(
        id=new_id,
        title=req.title.strip(),
        description=req.description.strip(),
        category_id=req.category_id,
        time_limit_minutes=req.time_limit_minutes,
        passing_score=req.passing_score,
        is_premium=req.is_premium,
        is_active=req.is_active,
        question_ids=question_ids
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)

    return APIResponse(
        message="Tạo đề thi mới thành công",
        data=ExamResponse(
            id=exam.id,
            title=exam.title,
            description=exam.description,
            category_id=exam.category_id,
            time_limit_minutes=exam.time_limit_minutes,
            passing_score=exam.passing_score,
            is_premium=exam.is_premium,
            is_active=exam.is_active,
            questions_count=len(exam.question_ids),
            question_ids=exam.question_ids
        )
    )


@router.put("/exams/{exam_id}", response_model=APIResponse[ExamResponse])
async def update_exam_admin(
    exam_id: int,
    req: ExamUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Cập nhật đề thi."""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi.")

    if req.title is not None:
        exam.title = req.title.strip()
    if req.description is not None:
        exam.description = req.description.strip()
    if req.category_id is not None:
        exam.category_id = req.category_id
    if req.time_limit_minutes is not None:
        exam.time_limit_minutes = req.time_limit_minutes
    if req.passing_score is not None:
        exam.passing_score = req.passing_score
    if req.is_premium is not None:
        exam.is_premium = req.is_premium
    if req.is_active is not None:
        exam.is_active = req.is_active
    if req.question_ids is not None:
        exam.question_ids = req.question_ids

    await db.commit()
    await db.refresh(exam)

    return APIResponse(
        message="Cập nhật đề thi thành công",
        data=ExamResponse(
            id=exam.id,
            title=exam.title,
            description=exam.description,
            category_id=exam.category_id,
            time_limit_minutes=exam.time_limit_minutes,
            passing_score=exam.passing_score,
            is_premium=exam.is_premium,
            is_active=exam.is_active,
            questions_count=len(exam.question_ids),
            question_ids=exam.question_ids
        )
    )


@router.delete("/exams/{exam_id}", response_model=APIResponse[dict])
async def delete_exam_admin(
    exam_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Xóa đề thi."""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi.")
    await db.delete(exam)
    await db.commit()
    return APIResponse(message=f"Đã xóa đề thi #{exam_id}")


# =========================================================================
# 4. ADMIN ROADMAP MANAGEMENT (QUẢN LÝ LỘ TRÌNH HỌC TẬP ROADMAPS)
# =========================================================================

@router.get("/roadmaps", response_model=APIResponse[List[RoadmapResponse]])
async def list_roadmaps_admin(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Xem danh sách toàn bộ lộ trình học tập."""
    stmt = select(Roadmap).order_by(Roadmap.display_order.asc())
    roadmaps = (await db.execute(stmt)).scalars().all()
    return APIResponse(data=[RoadmapResponse.model_validate(r) for r in roadmaps])


@router.post("/roadmaps", response_model=APIResponse[RoadmapResponse], status_code=status.HTTP_201_CREATED)
async def create_roadmap_admin(
    req: RoadmapCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Tạo lộ trình học tập mới."""
    existing = await db.get(Roadmap, req.id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Mã lộ trình '{req.id}' đã tồn tại.")

    roadmap = Roadmap(
        id=req.id.strip(),
        title=req.title.strip(),
        subtitle=req.subtitle.strip(),
        target_role=req.target_role.strip(),
        duration_weeks=req.duration_weeks,
        phases=req.phases,
        is_active=req.is_active,
        display_order=req.display_order
    )
    db.add(roadmap)
    await db.commit()
    await db.refresh(roadmap)

    return APIResponse(
        message="Tạo lộ trình học tập thành công",
        data=RoadmapResponse.model_validate(roadmap)
    )


@router.put("/roadmaps/{roadmap_id}", response_model=APIResponse[RoadmapResponse])
async def update_roadmap_admin(
    roadmap_id: str,
    req: RoadmapUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Cập nhật lộ trình học tập."""
    roadmap = await db.get(Roadmap, roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail="Không tìm thấy lộ trình.")

    if req.title is not None:
        roadmap.title = req.title.strip()
    if req.subtitle is not None:
        roadmap.subtitle = req.subtitle.strip()
    if req.target_role is not None:
        roadmap.target_role = req.target_role.strip()
    if req.duration_weeks is not None:
        roadmap.duration_weeks = req.duration_weeks
    if req.phases is not None:
        roadmap.phases = req.phases
    if req.is_active is not None:
        roadmap.is_active = req.is_active
    if req.display_order is not None:
        roadmap.display_order = req.display_order

    await db.commit()
    await db.refresh(roadmap)
    return APIResponse(
        message="Cập nhật lộ trình thành công",
        data=RoadmapResponse.model_validate(roadmap)
    )


@router.delete("/roadmaps/{roadmap_id}", response_model=APIResponse[dict])
async def delete_roadmap_admin(
    roadmap_id: str,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Xóa lộ trình học tập."""
    roadmap = await db.get(Roadmap, roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail="Không tìm thấy lộ trình.")
    await db.delete(roadmap)
    await db.commit()
    return APIResponse(message=f"Đã xóa lộ trình '{roadmap_id}'")


# =========================================================================
# 5. ADMIN BANNER MANAGEMENT (QUẢN LÝ BANNER QUẢNG BÁ / SỰ KIỆN)
# =========================================================================

@router.get("/banners", response_model=APIResponse[List[BannerResponse]])
async def list_banners_admin(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Xem danh sách toàn bộ banner."""
    stmt = select(Banner).order_by(Banner.display_order.asc())
    banners = (await db.execute(stmt)).scalars().all()
    return APIResponse(data=[BannerResponse.model_validate(b) for b in banners])


@router.post("/banners", response_model=APIResponse[BannerResponse], status_code=status.HTTP_201_CREATED)
async def create_banner_admin(
    req: BannerCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Tạo banner quảng bá mới."""
    max_id = (await db.execute(select(func.max(Banner.id)))).scalar_one() or 0
    new_id = max_id + 1

    banner = Banner(
        id=new_id,
        title=req.title.strip(),
        badge_text=req.badge_text.strip(),
        description=req.description.strip(),
        cta_text=req.cta_text.strip(),
        link_url=req.link_url.strip(),
        image_url=req.image_url,
        bg_gradient=req.bg_gradient,
        is_active=req.is_active,
        display_order=req.display_order
    )
    db.add(banner)
    await db.commit()
    await db.refresh(banner)

    return APIResponse(
        message="Tạo banner thành công",
        data=BannerResponse.model_validate(banner)
    )


@router.put("/banners/{banner_id}", response_model=APIResponse[BannerResponse])
async def update_banner_admin(
    banner_id: int,
    req: BannerUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Cập nhật banner."""
    banner = await db.get(Banner, banner_id)
    if not banner:
        raise HTTPException(status_code=404, detail="Không tìm thấy banner.")

    if req.title is not None:
        banner.title = req.title.strip()
    if req.badge_text is not None:
        banner.badge_text = req.badge_text.strip()
    if req.description is not None:
        banner.description = req.description.strip()
    if req.cta_text is not None:
        banner.cta_text = req.cta_text.strip()
    if req.link_url is not None:
        banner.link_url = req.link_url.strip()
    if req.image_url is not None:
        banner.image_url = req.image_url
    if req.bg_gradient is not None:
        banner.bg_gradient = req.bg_gradient
    if req.is_active is not None:
        banner.is_active = req.is_active
    if req.display_order is not None:
        banner.display_order = req.display_order

    await db.commit()
    await db.refresh(banner)

    return APIResponse(
        message="Cập nhật banner thành công",
        data=BannerResponse.model_validate(banner)
    )


@router.delete("/banners/{banner_id}", response_model=APIResponse[dict])
async def delete_banner_admin(
    banner_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """(Admin) Xóa banner."""
    banner = await db.get(Banner, banner_id)
    if not banner:
        raise HTTPException(status_code=404, detail="Không tìm thấy banner.")
    await db.delete(banner)
    await db.commit()
    return APIResponse(message=f"Đã xóa banner #{banner_id}")
