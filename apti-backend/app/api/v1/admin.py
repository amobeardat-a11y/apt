from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import require_admin
from app.models.user import User, SubscriptionTier, UserRole
from app.models.quiz import QuizAttempt, Question
from app.models.order import Order, OrderStatus
from app.schemas.user import UserResponse, UserAdminUpdate
from app.schemas.common import APIResponse, PaginatedResponse

router = APIRouter(prefix="/admin", tags=["Quản trị hệ thống (Admin Dashboard)"])


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

    return APIResponse(
        data={
            "total_users": total_users,
            "active_subscribers": active_subscribers,
            "total_revenue_vnd": int(total_revenue),
            "total_quizzes_taken": total_quizzes,
            "average_quiz_score": round(float(avg_score), 1),
            "total_questions_bank": total_questions,
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

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one() or 0

    # Pagination
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
        start = user.subscription_expires_at if (user.subscription_expires_at and user.subscription_expires_at > now) else now
        user.subscription_expires_at = start + timedelta(days=req.subscription_days_to_add)

    await db.commit()
    await db.refresh(user)
    return APIResponse(
        message="Cập nhật thông tin học viên thành công",
        data=UserResponse.model_validate(user)
    )

