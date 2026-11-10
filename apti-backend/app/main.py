import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.db.seed import seed_database
from app.core.middleware import (
    SecurityHeadersMiddleware,
    RequestTimingMiddleware,
    SafeExceptionMiddleware
)
from app.api.router import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("apti.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan:
    1. Connects to database (Neon PostgreSQL Serverless / SQLite Async).
    2. Synchronizes schema tables.
    3. Seeds initial data (Admin user, Quiz questions, Pricing plans, Documents).
    4. Cleans up database engine pool on shutdown.
    """
    logger.info(f"Đang khởi động {settings.PROJECT_NAME} v{settings.VERSION}...")
    logger.info(f"Môi trường: {settings.ENVIRONMENT} | Neon PostgreSQL Engine: {engine.url.render_as_string(hide_password=True)}")

    # Create tables if not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Cơ sở dữ liệu đã sẵn sàng và đồng bộ hóa các bảng thành công.")

    # Seed initial data
    async with AsyncSessionLocal() as session:
        try:
            await seed_database(session)
        except Exception as exc:
            logger.error(f"Lỗi khi khởi tạo dữ liệu mẫu: {exc}")

    yield

    logger.info("Đang đóng các kết nối cơ sở dữ liệu...")
    await engine.dispose()
    logger.info("Hệ thống APTI Backend đã dừng an toàn.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
## APTI Backend API - Nền tảng Ôn luyện Aptitude Test Tiếng Việt

Hệ thống Backend xây dựng trên **FastAPI**, tuân thủ nghiêm ngặt các tiêu chuẩn bảo mật **OWASP Top 10** và kết nối **Neon PostgreSQL Serverless**:

* **Bảo mật & Xác thực**: JWT Access Token & Refresh Token Rotation, Bcrypt Hashing, Chống Brute-force & Khóa tài khoản tạm thời.
* **Bảo vệ Đề thi**: Cắt bỏ đáp án đúng và lời giải trong luồng thi trắc nghiệm (chống F12 xem trước đáp án).
* **Phân quyền người dùng (RBAC)**: Học viên (User), Quản trị viên (Admin), Kiểm duyệt viên.
* **Gói học & Thanh toán**: Tích hợp mã VietQR Napas 24/7 tự động, xác thực chữ ký Webhook HMAC-SHA256.
* **Cơ sở dữ liệu**: Hỗ trợ đầy đủ Neon PostgreSQL Connection Pooling, SSL `sslmode=require`.
* **Giới hạn tần suất (Rate Limiting)**: Chống DDoS và Brute Force bằng Sliding Window Limiter.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. CORS Middleware (Bảo vệ nguồn truy cập tên miền chéo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time-Ms", "Retry-After"]
)

# 2. Security Headers Middleware (OWASP HSTS, CSP, X-Frame-Options, XSS, Nosniff)
app.add_middleware(SecurityHeadersMiddleware)

# 3. Request Latency Timing Middleware
app.add_middleware(RequestTimingMiddleware)

# 4. Global Safe Exception Handler (Chống rò rỉ stack trace và thông tin nội bộ hệ thống)
app.add_middleware(SafeExceptionMiddleware)

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Thông tin chung"])
async def root():
    return JSONResponse({
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "health_check": f"{settings.API_V1_STR}/health"
        },
        "description": "Hệ thống API Luyện thi Aptitude Test Tiếng Việt - APTI"
    })

