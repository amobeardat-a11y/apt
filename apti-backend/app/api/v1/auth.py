from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db
from app.core.rate_limiter import rate_limit_dependency, get_client_ip
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordChangeRequest
)
from app.schemas.user import UserResponse, UserProfileUpdate
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Xác thực & Bảo mật (Authentication)"])


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_dependency(max_requests=settings.RATE_LIMIT_AUTH_PER_MINUTE, window_seconds=60))]
)
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Đăng ký tài khoản học viên APTI mới.
    Áp dụng chính sách mật khẩu mạnh và giới hạn tần suất (Rate Limiting) để chống Spam.
    """
    user = await AuthService.register_user(db, req)
    return APIResponse(
        message="Đăng ký tài khoản APTI thành công! Bạn có thể đăng nhập ngay bây giờ.",
        data=UserResponse.model_validate(user)
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit_dependency(max_requests=settings.RATE_LIMIT_AUTH_PER_MINUTE, window_seconds=60))]
)
async def login(
    req: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Đăng nhập hệ thống APTI.
    Bảo vệ chống Brute-force: Tự động khóa tạm thời tài khoản sau 5 lần nhập sai liên tiếp.
    Trả về JWT Access Token (hết hạn 60p) và Refresh Token xoay vòng (Rotation).
    """
    ip = get_client_ip(request)
    device_info = request.headers.get("User-Agent")
    return await AuthService.authenticate_user(db, req, ip_address=ip, device_info=device_info)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit_dependency(max_requests=30, window_seconds=60))]
)
async def refresh_token(
    req: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Làm mới phiên đăng nhập (Refresh Token Rotation).
    Mã Refresh cũ sẽ bị thu hồi ngay lập tức để chống đánh cắp phiên.
    """
    ip = get_client_ip(request)
    device_info = request.headers.get("User-Agent")
    return await AuthService.refresh_access_token(
        db, req.refresh_token, ip_address=ip, device_info=device_info
    )


@router.post("/logout", response_model=APIResponse[None])
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Đăng xuất an toàn: Thu hồi toàn bộ Refresh Tokens của người dùng trên mọi thiết bị."""
    await AuthService.revoke_all_user_tokens(db, current_user.id)
    return APIResponse(message="Đăng xuất thành công. Phiên làm việc đã được đóng an toàn.")


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Lấy thông tin tài khoản và trạng thái gói học hiện tại của người dùng đang đăng nhập."""
    return APIResponse(
        message="Lấy thông tin hồ sơ thành công",
        data=UserResponse.model_validate(current_user)
    )


@router.put("/me", response_model=APIResponse[UserResponse])
async def update_my_profile(
    req: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật thông tin cá nhân (họ tên, số điện thoại, ảnh đại diện)."""
    if req.full_name:
        current_user.full_name = req.full_name.strip()
    if req.phone is not None:
        current_user.phone = req.phone.strip()
    if req.avatar_url is not None:
        current_user.avatar_url = req.avatar_url.strip()
    
    await db.commit()
    await db.refresh(current_user)
    return APIResponse(
        message="Cập nhật thông tin hồ sơ thành công",
        data=UserResponse.model_validate(current_user)
    )


@router.post("/change-password", response_model=APIResponse[None])
async def change_password(
    req: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Đổi mật khẩu tài khoản. Toàn bộ các phiên đăng nhập khác sẽ tự động bị đăng xuất để bảo mật."""
    await AuthService.change_password(db, current_user, req.current_password, req.new_password)
    return APIResponse(message="Đổi mật khẩu thành công. Vui lòng đăng nhập lại trên các thiết bị khác nếu cần.")

