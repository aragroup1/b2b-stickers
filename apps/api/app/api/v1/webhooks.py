from fastapi import APIRouter, Request, HTTPException, Header, Depends
from loguru import logger

from app.dependencies import get_db
from app.config import settings
from app.core.subscriptions.stripe_client import StripeClient
from app.services.email import EmailService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Track processed event IDs to prevent duplicate processing
_processed_event_ids: set[str] = set()


@router.post("/stripe")
async def stripe_webhook(request: Request, db=Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET not set — webhook verification impossible")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    try:
        event = StripeClient.construct_event(payload, sig_header)
    except Exception as e:
        logger.error(f"Stripe webhook verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_id = event["id"]
    event_type = event["type"]
    data = event["data"]["object"]

    # Idempotency check
    if event_id in _processed_event_ids:
        logger.info(f"Stripe event {event_id} already processed — skipping")
        return {"status": "already_processed"}
    _processed_event_ids.add(event_id)

    # Trim memory usage — keep only last 10k event IDs
    if len(_processed_event_ids) > 10000:
        _processed_event_ids.clear()

    logger.info(f"Stripe webhook: {event_type} (id={event_id})")

    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(data, db)
    elif event_type == "customer.subscription.updated":
        await _handle_subscription_updated(data, db)
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_deleted(data, db)
    elif event_type == "customer.updated":
        await _handle_customer_updated(data, db)
    elif event_type == "invoice.paid":
        await _handle_invoice_paid(data, db)
    elif event_type == "invoice.payment_failed":
        await _handle_invoice_payment_failed(data, db)

    return {"status": "ok"}


async def _handle_checkout_completed(data: dict, db):
    metadata = data.get("metadata", {})
    variant_id = int(metadata.get("variant_id", 0))
    customer_id = int(metadata.get("customer_id", 0))
    stripe_customer_id = data.get("customer")
    stripe_subscription_id = data.get("subscription")

    if not variant_id or not stripe_subscription_id:
        logger.warning("Missing metadata in checkout.session.completed")
        return

    # Get the subscription from Stripe to get price details
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    sub = stripe.Subscription.retrieve(stripe_subscription_id)

    price_id = sub["items"]["data"][0]["price"]["id"] if sub["items"]["data"] else None
    recurring_amount = sub["items"]["data"][0]["price"]["unit_amount"] / 100 if price_id else 0

    # Fetch customer shipping from DB
    customer_row = await db.fetchrow(
        "SELECT shipping_address, email FROM customers WHERE id = $1", customer_id
    )
    shipping_address = customer_row["shipping_address"] if customer_row else {}

    # Create subscription row
    await db.execute(
        """
        INSERT INTO subscriptions (
            customer_id, variant_id, stripe_subscription_id, stripe_price_id,
            recurring_amount, discount_percent, status,
            current_period_start, current_period_end, cancel_at_period_end, shipping_address
        )
        VALUES ($1, $2, $3, $4, $5, $6, 'active', $7, $8, $9, $10)
        ON CONFLICT (stripe_subscription_id) DO UPDATE SET
            status = EXCLUDED.status,
            current_period_start = EXCLUDED.current_period_start,
            current_period_end = EXCLUDED.current_period_end,
            cancel_at_period_end = EXCLUDED.cancel_at_period_end
        """,
        customer_id,
        variant_id,
        stripe_subscription_id,
        price_id,
        recurring_amount,
        settings.SUBSCRIBE_AND_SAVE_DISCOUNT_PERCENT,
        sub["current_period_start"],
        sub["current_period_end"],
        sub["cancel_at_period_end"],
        shipping_address,
    )

    # Send welcome email
    if customer_row:
        await EmailService.send_welcome(customer_row["email"])

    logger.info(f"Created subscription for customer {customer_id}, variant {variant_id}")


async def _handle_subscription_updated(data: dict, db):
    stripe_sub_id = data.get("id")
    status = data.get("status", "active")
    current_period_start = data.get("current_period_start")
    current_period_end = data.get("current_period_end")
    cancel_at_period_end = data.get("cancel_at_period_end", False)

    await db.execute(
        """
        UPDATE subscriptions
        SET status = $1, current_period_start = $2, current_period_end = $3,
            cancel_at_period_end = $4, updated_at = NOW()
        WHERE stripe_subscription_id = $5
        """,
        status, current_period_start, current_period_end, cancel_at_period_end, stripe_sub_id
    )

    logger.info(f"Updated subscription {stripe_sub_id} -> {status}")


async def _handle_subscription_deleted(data: dict, db):
    stripe_sub_id = data.get("id")
    await db.execute(
        "UPDATE subscriptions SET status = 'canceled', updated_at = NOW() WHERE stripe_subscription_id = $1",
        stripe_sub_id
    )
    logger.info(f"Canceled subscription {stripe_sub_id}")


async def _handle_customer_updated(data: dict, db):
    stripe_customer_id = data.get("id")
    shipping = data.get("shipping", {})

    await db.execute(
        "UPDATE customers SET shipping_address = $1 WHERE stripe_customer_id = $2",
        shipping, stripe_customer_id
    )
    logger.info(f"Updated customer shipping {stripe_customer_id}")


async def _handle_invoice_paid(data: dict, db):
    stripe_sub_id = data.get("subscription")
    if not stripe_sub_id:
        return

    # Find subscription
    row = await db.fetchrow(
        "SELECT * FROM subscriptions WHERE stripe_subscription_id = $1", stripe_sub_id
    )
    if not row:
        logger.warning(f"Invoice paid for unknown subscription {stripe_sub_id}")
        return

    # Schedule shipment for this period
    from datetime import date
    await db.execute(
        """
        INSERT INTO subscription_shipments (subscription_id, scheduled_for, variant_id, status)
        VALUES ($1, $2, $3, 'scheduled')
        ON CONFLICT (subscription_id, scheduled_for) DO NOTHING
        """,
        row["id"],
        date.today(),
        row["variant_id"],
    )

    # Send shipping notification
    customer_row = await db.fetchrow(
        "SELECT email FROM customers WHERE id = $1", row["customer_id"]
    )
    if customer_row:
        await EmailService.send_shipping_notification(customer_row["email"])

    logger.info(f"Scheduled shipment for subscription {row['id']}")


async def _handle_invoice_payment_failed(data: dict, db):
    stripe_sub_id = data.get("subscription")
    if stripe_sub_id:
        await db.execute(
            "UPDATE subscriptions SET status = 'past_due', updated_at = NOW() WHERE stripe_subscription_id = $1",
            stripe_sub_id
        )
        logger.info(f"Subscription {stripe_sub_id} marked past_due")


@router.post("/amazon")
async def amazon_webhook(request: Request):
    return {"status": "ok"}


@router.post("/ebay")
async def ebay_webhook(request: Request):
    return {"status": "ok"}
