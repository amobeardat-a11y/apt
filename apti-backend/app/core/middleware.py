import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("apti.security")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applies OWASP Recommended HTTP Security Headers to every response:
    - Defense against Clickjacking, MIME sniffing, XSS, Protocol Downgrades.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Adds execution timing header for performance & latency monitoring."""
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time-Ms"] = f"{process_time * 1000:.2f}"
        return response


class SafeExceptionMiddleware(BaseHTTPMiddleware):
    """
    Catches unexpected internal server errors to prevent leaking stack traces,
    Neon DB connection credentials, or internal schema structures to clients.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {exc}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "Đã xảy ra lỗi hệ thống. Đội ngũ kỹ thuật đã được thông báo để xử lý."
                }
            )

