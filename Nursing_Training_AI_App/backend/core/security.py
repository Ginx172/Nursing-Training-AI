from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.bucket = {}

    async def dispatch(self, request: Request, call_next: Callable):
        ip = request.client.host if request.client else "unknown"
        now = int(time.time())
        window = now // 60
        key = (ip, window)
        self.bucket[key] = self.bucket.get(key, 0) + 1
        if self.bucket[key] > self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Too Many Requests")
        return await call_next(request)


def validate_input_length(field_value: str, max_len: int = 4000):
    if field_value is None:
        return
    if len(field_value) > max_len:
        raise HTTPException(status_code=400, detail="Input too long")


