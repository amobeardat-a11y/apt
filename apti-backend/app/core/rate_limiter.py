import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Tuple
from fastapi import HTTPException, Request, status
from app.config import settings


class SlidingWindowRateLimiter:
    """
    In-memory thread-safe sliding window rate limiter.
    Guards API endpoints from brute force and denial of service.
    """
    def __init__(self):
        self._history: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        """
        Checks if request is allowed for the given key.
        Returns:
            (allowed: bool, remaining_requests: int, retry_after_seconds: int)
        """
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            # Clean up older timestamps outside the sliding window
            timestamps = [ts for ts in self._history[key] if ts > window_start]
            
            if len(timestamps) >= max_requests:
                # Rate limit exceeded
                oldest_timestamp = timestamps[0]
                retry_after = max(1, int(oldest_timestamp + window_seconds - now))
                self._history[key] = timestamps
                return False, 0, retry_after

            # Record this request
            timestamps.append(now)
            self._history[key] = timestamps
            remaining = max(0, max_requests - len(timestamps))
            return True, remaining, 0

    def cleanup(self):
        """Periodically cleans up stale keys from memory."""
        now = time.time()
        with self._lock:
            expired_keys = [
                key for key, ts in self._history.items()
                if not ts or ts[-1] < now - 300
            ]
            for key in expired_keys:
                del self._history[key]


rate_limiter = SlidingWindowRateLimiter()


def get_client_ip(request: Request) -> str:
    """Extracts real client IP even behind proxies (Cloudflare, Nginx, Fly.io, Neon)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "127.0.0.1"


def rate_limit_dependency(max_requests: int = 60, window_seconds: int = 60):
    """FastAPI Dependency for route-level rate limiting."""
    def dependency(request: Request):
        if not settings.RATE_LIMIT_ENABLED:
            return

        ip = get_client_ip(request)
        route_key = f"{ip}:{request.url.path}"
        allowed, remaining, retry_after = rate_limiter.is_allowed(
            route_key, max_requests=max_requests, window_seconds=window_seconds
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Quá nhiều yêu cầu. Vui lòng thử lại sau {retry_after} giây.",
                headers={"Retry-After": str(retry_after)}
            )
    return dependency

