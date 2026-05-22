from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.config import settings
from app.core.auth import (
    ADMIN_TOKEN_COOKIE,
    ADMIN_TOKEN_MAX_AGE_SECONDS,
    create_admin_token,
    require_admin,
    verify_admin_password,
)
from app.dependencies import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminLoginRequest(BaseModel):
    password: str


class AdminLoginResponse(BaseModel):
    success: bool
    expires_at: str


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(req: AdminLoginRequest, response: Response):
    """Authenticate as admin and set HTTP-only cookie."""
    if not verify_admin_password(req.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_admin_token()
    expires = datetime.utcnow() + timedelta(seconds=ADMIN_TOKEN_MAX_AGE_SECONDS)

    response.set_cookie(
        key=ADMIN_TOKEN_COOKIE,
        value=token,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        max_age=ADMIN_TOKEN_MAX_AGE_SECONDS,
        path="/",
    )

    return AdminLoginResponse(
        success=True,
        expires_at=expires.isoformat(),
    )


@router.post("/logout")
async def admin_logout(response: Response):
    """Clear the admin session cookie."""
    response.delete_cookie(
        key=ADMIN_TOKEN_COOKIE,
        path="/",
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
    )
    return {"success": True}


@router.get("/me")
async def admin_me(_=Depends(require_admin)):
    """Check if the current session is valid."""
    return {"authenticated": True, "role": "admin"}


@router.get("/")
async def admin_root(_=Depends(require_admin)):
    return {"message": "admin"}


@router.get("/settings")
async def get_settings(_=Depends(require_admin)):
    return {
        "subscribe_and_save_discount_percent": settings.SUBSCRIBE_AND_SAVE_DISCOUNT_PERCENT,
        "environment": settings.ENV,
    }
