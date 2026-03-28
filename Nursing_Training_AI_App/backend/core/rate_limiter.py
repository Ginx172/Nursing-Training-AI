"""
Rate Limiter - in-memory, thread-safe.
Limiteaza numarul de request-uri per IP per endpoint.
"""

import time
import threading
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status


class RateLimiter:
    """
    In-memory rate limiter cu sliding window.
    Thread-safe prin Lock.
    """

    def __init__(self):
        self._requests: Dict[str, list] = {}
        self._lock = threading.Lock()

    def _cleanup_old(self, key: str, window_seconds: int):
        """Sterge request-urile expirate din fereastra."""
        now = time.time()
        cutoff = now - window_seconds
        if key in self._requests:
            self._requests[key] = [t for t in self._requests[key] if t > cutoff]

    def check(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Verifica daca un request e permis.
        Returns: (allowed: bool, remaining: int)
        """
        with self._lock:
            self._cleanup_old(key, window_seconds)

            if key not in self._requests:
                self._requests[key] = []

            current_count = len(self._requests[key])

            if current_count >= max_requests:
                return False, 0

            self._requests[key].append(time.time())
            return True, max_requests - current_count - 1


# Singleton
rate_limiter = RateLimiter()


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    key_prefix: str = "api",
):
    """
    Dependency factory pentru rate limiting pe endpoint.

    Utilizare:
        @router.post("/login")
        async def login(request: Request, _rl=Depends(rate_limit(5, 300, "login"))):
            ...
    """
    async def _check(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        key = f"{key_prefix}:{client_ip}"
        allowed, remaining = rate_limiter.check(key, max_requests, window_seconds)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Try again in {window_seconds} seconds.",
                headers={"Retry-After": str(window_seconds)},
            )

    return _check
