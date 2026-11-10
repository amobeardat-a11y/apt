from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.base import ensure_utc
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    hash_token
)
from app.models.user import User, RefreshToken, UserRole, SubscriptionTier
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse


class AuthService:

    @staticmethod
    async def register_user(db: AsyncSession, req: RegisterRequest) -> User:
        # Check if email is already registered (case-insensitive)
        email_clean = req.email.lower().strip()
        stmt = select(User).where(User.email == email_clean)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email này đã được đăng ký. Vui lòng đăng nhập hoặc sử dụng email khác."
            )

        hashed = get_password_hash(req.password)
        new_user = User(
            email=email_clean,
            hashed_password=hashed,
            full_name=req.full_name.strip(),
            phone=req.phone.strip() if req.phone else None,
            role=UserRole.USER,
            is_active=True,
            is_verified=False,
            subscription_tier=SubscriptionTier.FREE
        )
        db.add(new_user)
        await db.flush()
        return new_user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        req: LoginRequest,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None
    ) -> TokenResponse:
        email_clean = req.email.lower().strip()
        stmt = select(User).where(User.email == email_clean)
        user = (await db.execute(stmt)).scalar_one_or_none()

        invalid_credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác.",
            headers={"WWW-Authenticate": "Bearer"}
        )

        if not user:
            # Constant-time comparison mitigation against timing attacks
            verify_password("dummy_password", "$2b$12$e80Yv8V0o456uF1R5j7eue73q4i4K.o1zD7O0E7q.9s.G4D0x32u.")
            raise invalid_credentials_exc

        # Check account lockout
        if user.is_locked:
            lock_seconds = max(1, int((ensure_utc(user.locked_until) - datetime.now(timezone.utc)).total_seconds()))
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Tài khoản bị tạm khóa do nhập sai quá nhiều lần. Vui lòng thử lại sau {lock_seconds} giây."
            )

        if not verify_password(req.password, user.hashed_password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
                await db.commit()
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Bạn đã nhập sai mật khẩu {settings.MAX_FAILED_LOGIN_ATTEMPTS} lần liên tiếp. Tài khoản bị tạm khóa trong {settings.ACCOUNT_LOCKOUT_MINUTES} phút."
                )
            await db.commit()
            raise invalid_credentials_exc

        # Reset failed login count and record login time
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)

        # Issue Access Token and Refresh Token
        access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
            claims={"email": user.email, "tier": user.subscription_tier.value}
        )
        raw_refresh, token_hash, expires_at = create_refresh_token()

        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            device_info=device_info
        )
        db.add(refresh_record)
        await db.commit()
        await db.refresh(user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        raw_refresh_token: str,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None
    ) -> TokenResponse:
        """
        Token Rotation:
        Validates current refresh token, marks it revoked, and issues a fresh pair.
        Prevents replay and token theft.
        """
        token_hash = hash_token(raw_refresh_token)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False
        )
        record = (await db.execute(stmt)).scalar_one_or_none()

        unauthorized_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên làm việc đã hết hạn hoặc mã làm mới không hợp lệ. Vui lòng đăng nhập lại."
        )

        if not record:
            raise unauthorized_exc

        if ensure_utc(record.expires_at) < datetime.now(timezone.utc):
            record.is_revoked = True
            await db.commit()
            raise unauthorized_exc

        # Revoke the used refresh token immediately (rotation)
        record.is_revoked = True

        # Fetch associated user
        user = await db.get(User, record.user_id)
        if not user or not user.is_active:
            raise unauthorized_exc

        # Issue new token pair
        new_access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
            claims={"email": user.email, "tier": user.subscription_tier.value}
        )
        new_raw_refresh, new_token_hash, new_expires_at = create_refresh_token()

        new_record = RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=new_expires_at,
            ip_address=ip_address,
            device_info=device_info
        )
        db.add(new_record)
        await db.commit()
        await db.refresh(user)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_raw_refresh,
            token_type="bearer",
            expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    async def revoke_all_user_tokens(db: AsyncSession, user_id: int):
        """Revokes all active refresh tokens for the user (used on logout and password change)."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
            .values(is_revoked=True)
        )
        await db.execute(stmt)
        await db.commit()

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ):
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu hiện tại không chính xác."
            )
        
        user.hashed_password = get_password_hash(new_password)
        # Invalidate all existing sessions on password change
        await AuthService.revoke_all_user_tokens(db, user.id)
        await db.commit()

