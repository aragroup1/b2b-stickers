from celery import shared_task
from loguru import logger
import asyncio

from app.config import settings
from app.core.subscriptions.fulfillment import SubscriptionFulfillment
from app.services.product_generation import ProductGenerationService
from app.services.email import EmailService
from app.database import init_pool, close_pool, get_pool


@shared_task
def sync_amazon_orders():
    logger.info("Syncing Amazon orders...")
    return {"synced": 0}


@shared_task
def sync_ebay_orders():
    logger.info("Syncing eBay orders...")
    return {"synced": 0}


@shared_task
def schedule_subscription_shipments():
    logger.info("Scheduling subscription shipments...")
    result = asyncio.run(SubscriptionFulfillment.schedule_monthly_shipments())
    return {"scheduled": len(result)}


@shared_task
def submit_scheduled_shipments():
    logger.info("Submitting scheduled shipments...")
    result = asyncio.run(SubscriptionFulfillment.submit_scheduled_shipments())
    return {"submitted": len(result)}


@shared_task
def sync_shipment_status():
    logger.info("Syncing shipment status...")
    result = asyncio.run(SubscriptionFulfillment.sync_shipment_status())
    return {"updated": len(result)}


@shared_task
def analytics_rollup():
    logger.info("Running analytics rollup...")
    return {"rolled_up": True}


@shared_task
def send_renewal_reminders():
    """Send renewal reminder emails 3 days before renewal."""
    logger.info("Sending renewal reminders...")

    async def _run():
        pool = await get_pool()
        rows = await pool.fetch(
            """
            SELECT s.id, s.current_period_end, c.email, c.name
            FROM subscriptions s
            JOIN customers c ON s.customer_id = c.id
            WHERE s.status = 'active'
              AND s.cancel_at_period_end = FALSE
              AND s.current_period_end BETWEEN NOW() + INTERVAL '3 days' AND NOW() + INTERVAL '4 days'
            """
        )

        sent = 0
        for row in rows:
            renewal_date = row["current_period_end"].strftime("%d %B %Y")
            success = await EmailService.send_renewal_reminder(row["email"], renewal_date)
            if success:
                sent += 1

        return {"reminders_sent": sent}

    return asyncio.run(_run())


@shared_task
def abandoned_cart_recovery():
    """Send recovery emails for abandoned carts."""
    logger.info("Running abandoned cart recovery...")

    async def _run():
        from app.api.v1.abandoned_cart import send_recovery_emails
        return await send_recovery_emails()

    return asyncio.run(_run())


@shared_task(bind=True)
def generate_batch(self, trend_ids: list[int], styles: list[str], designs_per_combo: int = 3, mode: str = "production"):
    async def _run():
        await init_pool()
        try:
            svc = ProductGenerationService()
            results = []
            for tid in trend_ids:
                ids = await svc.generate_from_trend(tid, styles, designs_per_combo, mode)
                results.extend(ids)

                # Update job progress using the shared pool
                pool = await get_pool()
                await pool.execute(
                    "UPDATE jobs SET progress = $1, updated_at = NOW() WHERE id = $2",
                    {"completed": len(results), "total": len(trend_ids) * len(styles) * designs_per_combo},
                    self.request.id,
                )

            return {"generated": len(results), "product_ids": results}
        finally:
            await close_pool()

    return asyncio.run(_run())
