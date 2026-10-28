import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    phone: Optional[str] = None

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Họ và tên phải có ít nhất 2 ký tự.")
        return clean

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Security Policy: Strong password requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 number
        - At least 1 special character
        """
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có tối thiểu 8 ký tự.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái in hoa (A-Z).")
        if not re.search(r"[a-z]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ cái thường (a-z).")
        if not re.search(r"\d", v):
            raise ValueError("Mật khẩu phải chứa ít nhất một chữ số (0-9).")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất một ký tự đặc biệt (!@#$%^&*...).")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu mới phải có ít nhất 8 ký tự.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Mật khẩu mới phải có chữ hoa.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Mật khẩu mới phải có chữ thường.")
        if not re.search(r"\d", v):
            raise ValueError("Mật khẩu mới phải có chữ số.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_]", v):
            raise ValueError("Mật khẩu mới phải có ký tự đặc biệt.")
        return v

