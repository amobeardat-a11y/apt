from typing import Optional
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db
from app.db.base import ensure_utc
from app.core.security import decode_token
from app.models.user import User, UserRole, SubscriptionTier

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Validates the JWT access token and returns the authenticated user.
    Enforces active account and brute-force lockout status.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception

    payload = decode_token(token)
    if not payload:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ hỗ trợ APTI."
        )

    if user.is_locked:
        lock_seconds = max(1, int((ensure_utc(user.locked_until) - datetime.now(timezone.utc)).total_seconds()))
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Tài khoản đang tạm khóa do nhập sai mật khẩu quá nhiều lần. Vui lòng chờ {lock_seconds} giây."
        )

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication: returns User if valid token provided, else None.
    Allows guest visitors to preview features while authenticated users get saved state.
    """
    if not token:
        return None
    try:
        return await get_current_user(token=token, db=db)
    except HTTPException:
        return None


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """RBAC Dependency: Requires ADMIN role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền quản trị viên (Admin) để thực hiện thao tác này."
        )
    return current_user


async def require_active_subscription(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency: Ensures user has an active paid subscription (Gói 7 Ngày / Gói 30 Ngày)."""
    if not current_user.has_active_subscription and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tính năng này yêu cầu Gói luyện tập APTI đang hoạt động (Gói 7 Ngày hoặc Gói 30 Ngày)."
        )
    return current_user

