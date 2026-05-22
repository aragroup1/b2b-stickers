from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from app.dependencies import get_db
from app.config import settings
from app.core.ai.generator import AIGenerator
from app.core.stickers.config import get_recurring_price
from app.core.subscriptions.pricing import compute_recurring_amount

router = APIRouter(prefix="/debug", tags=["debug"])


def _require_admin():
    """Simple admin gate — in production, replace with proper auth."""
    if settings.ENV == "production":
        raise HTTPException(status_code=403, detail="Debug endpoints disabled in production")


@router.post("/test-generation")
async def test_generation(
    keyword: str = Query("craft beer labels", description="Keyword to generate for"),
    style: str = Query("brewery_emblem", description="Style from prompt_templates.py"),
    mode: str = Query("testing", description="testing or production"),
    db=Depends(get_db),
):
    """Generate a single design end-to-end and return the full result.

    Protected: disabled in production. Burns Replicate credits.
    """
    _require_admin()
    generator = AIGenerator()

    try:
        result = await generator.generate(
            keyword=keyword,
            style=style,
            mode=mode,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "generation_failed",
            "message": str(e),
        })

    # Compute what the subscription price would be for a sample variant
    sample_retail = 4.99
    sample_recurring = compute_recurring_amount(sample_retail)

    return {
        "success": True,
        "keyword": keyword,
        "style": style,
        "mode": mode,
        "image_url": result["image_url"],
        "model_used": result["model_used"],
        "prompt": result["prompt"],
        "negative_prompt": result["negative_prompt"],
        "generation_cost": result["generation_cost"],
        "quality_score": result["quality_score"],
        "vision_warnings": result.get("vision_warnings", []),
        "attributes": result.get("attributes", {}),
        "sample_pricing": {
            "retail": sample_retail,
            "recurring_with_10_discount": sample_recurring,
        },
    }


@router.get("/test-catalog-variant/{slug}")
async def test_catalog_variant(slug: str, db=Depends(get_db)):
    """Fetch a product from the catalog and show its variant pricing."""
    _require_admin()
    row = await db.fetchrow(
        """
        SELECT p.id, p.slug, p.title, a.image_url
        FROM products p
        JOIN artwork a ON p.artwork_id = a.id
        WHERE p.slug = $1 AND p.status = 'approved'
        """,
        slug,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    variants = await db.fetch(
        "SELECT * FROM sticker_variants WHERE product_id = $1",
        row["id"]
    )

    product = dict(row)
    product["variants"] = []
    for v in variants:
        vd = dict(v)
        vd["recurring_price"] = get_recurring_price(v["retail_price"])
        product["variants"].append(vd)

    return product


@router.post("/test-stripe-checkout")
async def test_stripe_checkout(
    variant_id: int = Query(1, description="Variant ID to subscribe to"),
    email: str = Query("test@example.com", description="Customer email"),
    db=Depends(get_db),
):
    """Test the Stripe checkout flow for a given variant."""
    _require_admin()
    from app.core.subscriptions.stripe_client import StripeClient

    variant = await db.fetchrow(
        "SELECT * FROM sticker_variants WHERE id = $1", variant_id
    )
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Create or get customer
    customer_row = await db.fetchrow(
        "SELECT * FROM customers WHERE email = $1", email
    )

    if customer_row and customer_row["stripe_customer_id"]:
        stripe_customer_id = customer_row["stripe_customer_id"]
    else:
        stripe_customer = StripeClient.create_customer(email=email)
        stripe_customer_id = stripe_customer.id
        if customer_row:
            await db.execute(
                "UPDATE customers SET stripe_customer_id = $1 WHERE id = $2",
                stripe_customer_id, customer_row["id"]
            )
        else:
            await db.fetchval(
                "INSERT INTO customers (email, stripe_customer_id) VALUES ($1, $2) RETURNING id",
                email, stripe_customer_id
            )

    # Create price
    recurring_amount = compute_recurring_amount(variant["retail_price"])
    unit_amount_pence = int(round(recurring_amount * 100))

    stripe_price = StripeClient.get_or_create_price(
        variant_id=variant["id"],
        sku=variant["sku"],
        unit_amount_pence=unit_amount_pence,
    )

    # Create checkout session
    session = StripeClient.create_checkout_session(
        customer_id=stripe_customer_id,
        price_id=stripe_price.id,
        success_url=f"{settings.SITE_BASE_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.SITE_BASE_URL}/shop",
        metadata={
            "variant_id": str(variant["id"]),
            "sku": variant["sku"],
        },
    )

    return {
        "checkout_url": session.url,
        "stripe_price_id": stripe_price.id,
        "recurring_amount": recurring_amount,
        "variant": dict(variant),
    }


@router.post("/test-fulfillment")
async def test_fulfillment(
    order_id: int = Query(1, description="Order ID to fulfill"),
):
    """Test the print provider fulfillment flow."""
    _require_admin()
    from app.core.print_provider import get_print_provider

    provider = get_print_provider()

    # Get a mock quote
    quote = await provider.quote(variant_id=1, quantity=1)

    return {
        "provider": provider.__class__.__name__,
        "quote": quote,
        "note": "Use POST /orders/{id}/fulfill to submit a real order",
    }
