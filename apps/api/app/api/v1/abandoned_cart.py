from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta

from app.dependencies import get_db
from app.services.email import EmailService

router = APIRouter(prefix="/abandoned-cart", tags=["abandoned-cart"])


class CartEventRequest(BaseModel):
    email: EmailStr
    variant_id: int


@router.post("/track")
async def track_abandoned_cart(req: CartEventRequest, db=Depends(get_db)):
    """Record an abandoned cart event."""
    # Upsert abandoned cart record
    await db.execute(
        """
        INSERT INTO abandoned_carts (customer_email, variant_id)
        VALUES ($1, $2)
        ON CONFLICT DO NOTHING
        """,
        req.email, req.variant_id,
    )
    return {"status": "tracked"}


@router.post("/recover")
async def send_recovery_emails(db=Depends(get_db)):
    """Send recovery emails for abandoned carts (run via Celery beat)."""
    # Find carts abandoned 1-24 hours ago that haven't been reminded
    rows = await db.fetch(
        """
        SELECT ac.*, sv.size_inches, sv.pack_quantity, sv.retail_price,
               p.title as product_title, p.slug as product_slug
        FROM abandoned_carts ac
        JOIN sticker_variants sv ON ac.variant_id = sv.id
        JOIN products p ON sv.product_id = p.id
        WHERE ac.reminder_sent = FALSE
          AND ac.recovered = FALSE
          AND ac.created_at BETWEEN NOW() - INTERVAL '24 hours' AND NOW() - INTERVAL '1 hour'
        LIMIT 100
        """
    )

    sent = 0
    for row in rows:
        # Get variant pricing
        from app.core.stickers.config import get_recurring_price, compute_vat_inclusive_price
        recurring = get_recurring_price(row["retail_price"])
        recurring_vat = compute_vat_inclusive_price(recurring)

        # Send recovery email
        product_url = f"/product/{row['product_slug']}"
        email_sent = await EmailService.send_recovery_email(
            email=row["customer_email"],
            product_title=row["product_title"],
            product_url=product_url,
            size=row["size_inches"],
            pack=row["pack_quantity"],
            price=recurring_vat,
        )

        if email_sent:
            await db.execute(
                "UPDATE abandoned_carts SET reminder_sent = TRUE WHERE id = $1",
                row["id"],
            )
            sent += 1

    return {"reminders_sent": sent}
