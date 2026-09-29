import time
import secrets
from collections import defaultdict, deque
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException, status
from app.config import (
    AUTH_ENABLED, AUTH_PASSWORD, AUTH_COOKIE_NAME,
    RATE_LIMIT_MAX_ATTEMPTS, RATE_LIMIT_WINDOW_SECONDS
)

class RateLimiter:
    def __init__(self, max_attempts: int = RATE_LIMIT_MAX_ATTEMPTS, window_seconds: int = RATE_LIMIT_WINDOW_SECONDS):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts: Dict[str, deque] = defaultdict(deque)

    def check_limit(self, ip: str) -> Tuple[bool, int]:
        """
        Check if IP is allowed to attempt login.
        Returns: (is_allowed, remaining_attempts_or_retry_after)
        """
        now = time.time()
        q = self.attempts[ip]

        # Clean up timestamps older than window
        while q and q[0] <= now - self.window_seconds:
            q.popleft()

        if len(q) >= self.max_attempts:
            # Blocked: calculate seconds until oldest attempt expires
            retry_after = int(self.window_seconds - (now - q[0]))
            return False, max(1, retry_after)

        remaining = self.max_attempts - len(q)
        return True, remaining

    def record_failure(self, ip: str):
        """Record a failed login attempt for an IP"""
        now = time.time()
        self.attempts[ip].append(now)

    def reset(self, ip: str):
        """Reset attempts on successful login"""
        if ip in self.attempts:
            del self.attempts[ip]

# In-memory session store: token -> expiry timestamp (7 days)
SESSION_DURATION_SECONDS = 7 * 24 * 3600
active_sessions: Dict[str, float] = {}

rate_limiter = RateLimiter()

def get_client_ip(request: Request) -> str:
    """Extract real client IP handling reverse proxy headers"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "127.0.0.1"

def create_session() -> str:
    token = secrets.token_urlsafe(32)
    active_sessions[token] = time.time() + SESSION_DURATION_SECONDS
    return token

def verify_token(token: Optional[str]) -> bool:
    if not AUTH_ENABLED:
        return True
    if not token or token not in active_sessions:
        return False
    # Check expiry
    if active_sessions[token] < time.time():
        del active_sessions[token]
        return False
    return True

def delete_session(token: Optional[str]):
    if token and token in active_sessions:
        del active_sessions[token]

def require_auth(request: Request):
    """Dependency for protecting REST API endpoints"""
    if not AUTH_ENABLED:
        return True

    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token:
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

    if not token:
        # Check query param
        token = request.query_params.get("token")

    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu đăng nhập mật khẩu để tiếp tục"
        )
    return True
