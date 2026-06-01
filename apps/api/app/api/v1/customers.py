from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt
from loguru import logger

from app.dependencies import get_db
from app.config import settings
from app.services.email import EmailService
from app.core.auth import require_admin

router = APIRouter(prefix="/customers", tags=["customers"])


def _create_magic_link_token(email: str) -> str:
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "type": "magic_link",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def _verify_magic_link_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "magic_link":
            raise ValueError("Invalid token type")
        return payload["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")


def _create_session_token(customer_id: int, email: str) -> str:
    payload = {
        "customer_id": customer_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=30),
        "type": "session",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


async def _get_customer_from_request(request: Request, db) -> dict:
    auth = request.cookies.get("session")
    if not auth:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(auth, settings.JWT_SECRET, algorithms=["HS256"])
        row = await db.fetchrow("SELECT * FROM customers WHERE id = $1", payload["customer_id"])
        if not row:
            raise HTTPException(status_code=401, detail="Customer not found")
        return dict(row)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session")


class MagicLinkRequest(BaseModel):
    email: EmailStr


@router.post("/auth/magic-link")
async def request_magic_link(req: MagicLinkRequest, db=Depends(get_db)):
    token = _create_magic_link_token(req.email)
    link = f"{settings.MAGIC_LINK_BASE_URL}/api/auth/callback?token={token}"

    # Send actual email
    sent = await EmailService.send_magic_link(req.email, link)
    if not sent and settings.ENV == "development":
        logger.info(f"[DEV] Magic link for {req.email}: {link}")

    return {
        "status": "sent" if sent else "queued",
        "link": link if settings.ENV == "development" and not sent else None,
    }


@router.get("/auth/callback")
async def magic_link_callback(token: str, db=Depends(get_db)):
    email = _verify_magic_link_token(token)

    row = await db.fetchrow("SELECT * FROM customers WHERE email = $1", email)
    if row:
        customer_id = row["id"]
    else:
        customer_id = await db.fetchval(
            "INSERT INTO customers (email) VALUES ($1) RETURNING id", email
        )

    session_token = _create_session_token(customer_id, email)

    from fastapi.responses import RedirectResponse
    response = RedirectResponse(url=f"{settings.SITE_BASE_URL}/account")
    response.set_cookie(
        "session",
        session_token,
        httponly=True,
        max_age=2592000,
        secure=settings.ENV == "production",
        samesite="lax",
    )
    return response


@router.get("/me")
async def me(request: Request, db=Depends(get_db)):
    customer = await _get_customer_from_request(request, db)
    return customer


@router.get("/me/subscriptions")
async def my_subscriptions(request: Request, db=Depends(get_db)):
    customer = await _get_customer_from_request(request, db)
    rows = await db.fetch(
        """
        SELECT s.*, sv.size_inches, sv.pack_quantity, sv.sku,
               p.title as product_title, p.slug as product_slug
        FROM subscriptions s
        JOIN sticker_variants sv ON s.variant_id = sv.id
        JOIN products p ON sv.product_id = p.id
        WHERE s.customer_id = $1
        ORDER BY s.created_at DESC
        """,
        customer["id"]
    )
    return {"subscriptions": [dict(r) for r in rows]}


@router.get("/me/shipments")
async def my_shipments(request: Request, db=Depends(get_db)):
    customer = await _get_customer_from_request(request, db)
    rows = await db.fetch(
        """
        SELECT ss.*, sv.sku, p.title as product_title
        FROM subscription_shipments ss
        JOIN subscriptions s ON ss.subscription_id = s.id
        JOIN sticker_variants sv ON ss.variant_id = sv.id
        JOIN products p ON sv.product_id = p.id
        WHERE s.customer_id = $1
        ORDER BY ss.scheduled_for DESC
        """,
        customer["id"]
    )
    return {"shipments": [dict(r) for r in rows]}


@router.get("")
async def list_customers(
    limit: int = 100,
    offset: int = 0,
    db=Depends(get_db),
    _=Depends(require_admin),
):
    rows = await db.fetch(
        "SELECT * FROM customers ORDER BY created_at DESC LIMIT $1 OFFSET $2",
        limit, offset
    )
    return {"customers": [dict(r) for r in rows]}
