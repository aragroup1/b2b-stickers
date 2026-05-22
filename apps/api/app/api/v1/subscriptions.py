from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.dependencies import get_db
from app.config import settings
from app.core.auth import require_admin
from app.core.subscriptions.stripe_client import StripeClient
from app.core.subscriptions.pricing import compute_recurring_amount

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class ShippingAddress(BaseModel):
    name: str
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str = "GB"


class CheckoutRequest(BaseModel):
    variant_id: int
    email: EmailStr
    shipping_address: ShippingAddress


@router.post("/checkout")
async def checkout(req: CheckoutRequest, db=Depends(get_db)):
    # Get variant
    variant = await db.fetchrow(
        "SELECT * FROM sticker_variants WHERE id = $1", req.variant_id
    )
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Get or create customer
    customer_row = await db.fetchrow(
        "SELECT * FROM customers WHERE email = $1", req.email
    )

    customer_id: int

    if customer_row and customer_row["stripe_customer_id"]:
        stripe_customer_id = customer_row["stripe_customer_id"]
        customer_id = customer_row["id"]
        # Update shipping address
        await db.execute(
            "UPDATE customers SET shipping_address = $1 WHERE id = $2",
            req.shipping_address.model_dump(), customer_id
        )
    else:
        # Create Stripe customer
        stripe_customer = StripeClient.create_customer(
            email=req.email,
            shipping={
                "name": req.shipping_address.name,
                "address": {
                    "line1": req.shipping_address.line1,
                    "line2": req.shipping_address.line2 or "",
                    "city": req.shipping_address.city,
                    "state": req.shipping_address.state or "",
                    "postal_code": req.shipping_address.postal_code,
                    "country": req.shipping_address.country,
                },
            },
        )
        stripe_customer_id = stripe_customer.id

        # Upsert customer in DB
        if customer_row:
            await db.execute(
                "UPDATE customers SET stripe_customer_id = $1, shipping_address = $2 WHERE id = $3",
                stripe_customer_id, req.shipping_address.model_dump(), customer_row["id"]
            )
            customer_id = customer_row["id"]
        else:
            customer_id = await db.fetchval(
                """
                INSERT INTO customers (email, stripe_customer_id, shipping_address)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                req.email, stripe_customer_id, req.shipping_address.model_dump()
            )

    # Create dynamic Price for this variant
    recurring_amount = compute_recurring_amount(variant["retail_price"])
    unit_amount_pence = int(round(recurring_amount * 100))

    stripe_price = StripeClient.get_or_create_price(
        variant_id=variant["id"],
        sku=variant["sku"],
        unit_amount_pence=unit_amount_pence,
    )

    # Create Checkout session
    success_url = f"{settings.SITE_BASE_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{settings.SITE_BASE_URL}/shop"

    session = StripeClient.create_checkout_session(
        customer_id=stripe_customer_id,
        price_id=stripe_price.id,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "variant_id": str(variant["id"]),
            "customer_id": str(customer_id),
            "sku": variant["sku"],
        },
    )

    return {"checkout_url": session.url}


@router.get("/portal")
async def portal(request: Request, db=Depends(get_db)):
    # In production, authenticate via JWT/magic-link cookie
    # For now, require customer_id as query param
    customer_id = request.query_params.get("customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id required")

    row = await db.fetchrow(
        "SELECT stripe_customer_id FROM customers WHERE id = $1", int(customer_id)
    )
    if not row or not row["stripe_customer_id"]:
        raise HTTPException(status_code=404, detail="Customer not found")

    portal_session = StripeClient.create_portal_session(
        customer_id=row["stripe_customer_id"],
        return_url=f"{settings.SITE_BASE_URL}/account",
    )

    return {"portal_url": portal_session.url}


@router.get("/")
async def list_subscriptions(db=Depends(get_db), _=Depends(require_admin)):
    rows = await db.fetch("SELECT * FROM subscriptions ORDER BY created_at DESC LIMIT 100")
    return {"subscriptions": [dict(r) for r in rows]}


@router.get("/{id}")
async def get_subscription(id: int, db=Depends(get_db), _=Depends(require_admin)):
    row = await db.fetchrow("SELECT * FROM subscriptions WHERE id = $1", id)
    if not row:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return dict(row)
