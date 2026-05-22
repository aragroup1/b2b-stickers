from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.dependencies import get_db
from app.config import settings
from app.core.subscriptions.stripe_client import StripeClient
from app.core.stickers.config import compute_vat_inclusive_price, compute_vat_amount

router = APIRouter(prefix="/onetime", tags=["onetime"])


class OnetimeCheckoutRequest(BaseModel):
    variant_id: int
    email: EmailStr
    quantity: int = 1
    shipping_address: dict


@router.post("/checkout")
async def onetime_checkout(req: OnetimeCheckoutRequest, db=Depends(get_db)):
    """Create a one-time purchase checkout session."""
    variant = await db.fetchrow(
        "SELECT * FROM sticker_variants WHERE id = $1", req.variant_id
    )
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Check stock
    if variant["stock_quantity"] < req.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {variant['stock_quantity']} units in stock"
        )

    # Get or create customer
    customer_row = await db.fetchrow(
        "SELECT * FROM customers WHERE email = $1", req.email
    )

    customer_id: int
    if customer_row and customer_row["stripe_customer_id"]:
        stripe_customer_id = customer_row["stripe_customer_id"]
        customer_id = customer_row["id"]
    else:
        stripe_customer = StripeClient.create_customer(
            email=req.email,
            shipping=req.shipping_address,
        )
        stripe_customer_id = stripe_customer.id

        if customer_row:
            await db.execute(
                "UPDATE customers SET stripe_customer_id = $1 WHERE id = $2",
                stripe_customer_id, customer_row["id"]
            )
            customer_id = customer_row["id"]
        else:
            customer_id = await db.fetchval(
                """
                INSERT INTO customers (email, stripe_customer_id, shipping_address)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                req.email, stripe_customer_id, req.shipping_address
            )

    # Calculate pricing with VAT
    unit_price = float(variant["retail_price"])
    vat_per_unit = compute_vat_amount(unit_price, settings.VAT_RATE_PERCENT)
    total_ex_vat = unit_price * req.quantity
    total_vat = vat_per_unit * req.quantity
    total_inc_vat = compute_vat_inclusive_price(total_ex_vat, settings.VAT_RATE_PERCENT)

    # Create Stripe Checkout session for one-time payment
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        customer=stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "gbp",
                "product_data": {
                    "name": f"Stickers — {variant['size_inches']}\" Pack of {variant['pack_quantity']}",
                    "metadata": {"variant_id": str(variant["id"]), "sku": variant["sku"]},
                },
                "unit_amount": int(round(total_inc_vat / req.quantity * 100)),  # pence inc VAT
            },
            "quantity": req.quantity,
        }],
        mode="payment",
        success_url=f"{settings.SITE_BASE_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}&type=onetime",
        cancel_url=f"{settings.SITE_BASE_URL}/shop",
        metadata={
            "variant_id": str(variant["id"]),
            "customer_id": str(customer_id),
            "quantity": str(req.quantity),
            "type": "onetime",
        },
    )

    # Record the pending order
    await db.execute(
        """
        INSERT INTO onetime_purchases (customer_id, variant_id, quantity, unit_price, vat_amount, total_price, stripe_payment_intent_id, shipping_address, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'pending')
        """,
        customer_id, variant["id"], req.quantity, unit_price, total_vat, total_inc_vat,
        session.payment_intent, req.shipping_address,
    )

    return {"checkout_url": session.url}


@router.post("/webhook")
async def onetime_webhook(request: Request, db=Depends(get_db)):
    """Handle Stripe webhook for one-time payment completion."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        data = event["data"]["object"]
        metadata = data.get("metadata", {})

        if metadata.get("type") == "onetime":
            payment_intent = data.get("payment_intent")

            # Update order status
            await db.execute(
                "UPDATE onetime_purchases SET status = 'paid' WHERE stripe_payment_intent_id = $1",
                payment_intent,
            )

            # Deduct stock
            variant_id = int(metadata.get("variant_id", 0))
            quantity = int(metadata.get("quantity", 1))
            await db.execute(
                "UPDATE sticker_variants SET stock_quantity = stock_quantity - $1 WHERE id = $2",
                quantity, variant_id,
            )

            # Create unified order record
            customer_id = int(metadata.get("customer_id", 0))
            purchase = await db.fetchrow(
                "SELECT * FROM onetime_purchases WHERE stripe_payment_intent_id = $1",
                payment_intent,
            )

            if purchase:
                await db.execute(
                    """
                    INSERT INTO orders (source, customer_id, variant_id, order_value, vat_amount, order_total, fulfillment_status, shipping_address)
                    VALUES ('onetime_store', $1, $2, $3, $4, $5, 'pending', $6)
                    """,
                    customer_id, variant_id, purchase["unit_price"] * quantity,
                    purchase["vat_amount"], purchase["total_price"], purchase["shipping_address"],
                )

    return {"status": "ok"}
