"""Admin authentication utilities."""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, Request, status
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_TOKEN_COOKIE = "admin_session"
ADMIN_TOKEN_MAX_AGE_SECONDS = 8 * 3600  # 8 hours


def verify_admin_password(plain_password: str) -> bool:
    """Verify the admin password against the configured hash."""
    if not settings.ADMIN_PASSWORD_HASH:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication not configured",
        )
    return pwd_context.verify(plain_password, settings.ADMIN_PASSWORD_HASH)


def create_admin_token() -> str:
    """Create a short-lived JWT for admin sessions."""
    payload = {
        "role": "admin",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=ADMIN_TOKEN_MAX_AGE_SECONDS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def verify_admin_token(token: str) -> bool:
    """Verify an admin JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload.get("role") == "admin"
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


def _extract_token_from_request(request: Request) -> Optional[str]:
    """Extract admin token from cookie or Authorization header."""
    # Try cookie first
    token = request.cookies.get(ADMIN_TOKEN_COOKIE)
    if token:
        return token

    # Try Authorization header (Bearer token)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]

    return None


async def require_admin(request: Request) -> None:
    """FastAPI dependency: raise 401 if the request lacks a valid admin token."""
    token = _extract_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_admin_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin session",
            headers={"WWW-Authenticate": "Bearer"},
        )
