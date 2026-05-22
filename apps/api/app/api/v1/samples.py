from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

from app.dependencies import get_db
from app.config import settings
from app.core.subscriptions.stripe_client import StripeClient

router = APIRouter(prefix="/samples", tags=["samples"])


class SampleRequest(BaseModel):
    product_id: int
    email: EmailStr
    shipping_address: dict


@router.post("/order")
async def order_sample(req: SampleRequest, db=Depends(get_db)):
    """Order a sample pack of stickers."""
    product = await db.fetchrow(
        "SELECT * FROM products WHERE id = $1 AND status = 'approved'", req.product_id
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get or create customer
    customer_row = await db.fetchrow(
        "SELECT * FROM customers WHERE email = $1", req.email
    )

    customer_id: int
    if customer_row:
        customer_id = customer_row["id"]
    else:
        customer_id = await db.fetchval(
            "INSERT INTO customers (email, shipping_address) VALUES ($1, $2) RETURNING id",
            req.email, req.shipping_address,
        )

    # Sample pricing: flat £2.99 inc shipping (or free for UK businesses)
    sample_price = 2.99

    # Create Stripe payment intent for sample
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "gbp",
                "product_data": {
                    "name": f"Sample Pack — {product['title']}",
                },
                "unit_amount": int(round(sample_price * 100)),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{settings.SITE_BASE_URL}/checkout/success?type=sample",
        cancel_url=f"{settings.SITE_BASE_URL}/product/{product['slug']}",
        metadata={
            "product_id": str(req.product_id),
            "customer_id": str(customer_id),
            "type": "sample",
        },
    )

    # Record sample order
    await db.execute(
        """
        INSERT INTO sample_orders (customer_id, product_id, sample_sku, shipping_address, stripe_payment_intent_id)
        VALUES ($1, $2, $3, $4, $5)
        """,
        customer_id, req.product_id, f"SAMPLE-{req.product_id:05d}",
        req.shipping_address, session.payment_intent,
    )

    return {"checkout_url": session.url, "sample_price": sample_price}
