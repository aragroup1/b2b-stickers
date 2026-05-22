from datetime import date, timedelta
from typing import List

from loguru import logger

from app.database import get_pool
from app.core.print_provider import get_print_provider
from app.services.email import EmailService


class SubscriptionFulfillment:
    """Monthly shipment scheduler for active subscriptions."""

    @staticmethod
    async def schedule_monthly_shipments() -> List[int]:
        """Daily Celery beat job: create shipment rows for renewals due today."""
        pool = await get_pool()
        rows = await pool.fetch(
            """
            SELECT s.id, s.variant_id, s.current_period_start, s.current_period_end, c.email
            FROM subscriptions s
            JOIN customers c ON s.customer_id = c.id
            WHERE s.status = 'active'
              AND s.current_period_start <= CURRENT_DATE
              AND NOT EXISTS (
                SELECT 1 FROM subscription_shipments ss
                WHERE ss.subscription_id = s.id
                  AND ss.scheduled_for = s.current_period_start
              )
            """
        )

        shipment_ids = []
        for row in rows:
            sid = await pool.fetchval(
                """
                INSERT INTO subscription_shipments (subscription_id, scheduled_for, variant_id, status)
                VALUES ($1, $2, $3, 'scheduled')
                ON CONFLICT (subscription_id, scheduled_for) DO NOTHING
                RETURNING id
                """,
                row["id"],
                row["current_period_start"],
                row["variant_id"],
            )
            if sid:
                shipment_ids.append(sid)
                logger.info(f"Scheduled shipment {sid} for subscription {row['id']}")

        return shipment_ids

    @staticmethod
    async def submit_scheduled_shipments() -> List[int]:
        """Hourly job: pick scheduled shipments and submit to print provider."""
        pool = await get_pool()
        rows = await pool.fetch(
            """
            SELECT ss.id, ss.subscription_id, ss.variant_id,
                   s.shipping_address, c.email, c.name,
                   a.image_url, sv.size_inches, sv.pack_quantity
            FROM subscription_shipments ss
            JOIN subscriptions s ON ss.subscription_id = s.id
            JOIN customers c ON s.customer_id = c.id
            JOIN sticker_variants sv ON ss.variant_id = sv.id
            JOIN products p ON sv.product_id = p.id
            JOIN artwork a ON p.artwork_id = a.id
            WHERE ss.status = 'scheduled'
            LIMIT 100
            """
        )

        provider = get_print_provider()
        submitted = []

        for row in rows:
            shipping = row["shipping_address"] or {}
            if not shipping.get("line1"):
                logger.warning(f"Shipment {row['id']} has no shipping address — skipping")
                continue

            result = await provider.submit_order(
                order_id=row["id"],
                artwork_url=row["image_url"] or "",
                shipping=shipping,
                variant={
                    "id": row["variant_id"],
                    "size_inches": row["size_inches"],
                    "pack_quantity": row["pack_quantity"],
                },
                quantity=1,
            )

            if result.get("success"):
                await pool.execute(
                    """
                    UPDATE subscription_shipments
                    SET status = 'submitted',
                        print_provider_order_id = $1,
                        updated_at = NOW()
                    WHERE id = $2
                    """,
                    result["provider_order_id"], row["id"],
                )

                # Create unified order record
                await pool.execute(
                    """
                    INSERT INTO orders (source, customer_id, variant_id, subscription_shipment_id,
                                       fulfillment_provider, fulfillment_status, shipping_address)
                    VALUES ('subscription', $1, $2, $3, 'prodigi', 'processing', $4)
                    """,
                    row["subscription_id"], row["variant_id"], row["id"], shipping,
                )

                # Send shipping notification
                await EmailService.send_shipping_notification(
                    row["email"],
                    result.get("tracking", {}).get("trackingNumber"),
                )

                submitted.append(row["id"])
                logger.info(f"Submitted shipment {row['id']} to print provider")
            else:
                logger.error(f"Failed to submit shipment {row['id']}: {result.get('error')}")

        return submitted

    @staticmethod
    async def sync_shipment_status() -> List[dict]:
        """Check status of submitted shipments and update tracking."""
        pool = await get_pool()
        rows = await pool.fetch(
            """
            SELECT id, print_provider_order_id
            FROM subscription_shipments
            WHERE status = 'submitted'
            """
        )

        provider = get_print_provider()
        updates = []

        for row in rows:
            if not row["print_provider_order_id"]:
                continue

            status_result = await provider.get_status(row["print_provider_order_id"])
            new_status = status_result.get("status", "unknown")

            # Map Prodigi status to our status
            status_map = {
                "created": "submitted",
                "inproduction": "submitted",
                "shipped": "shipped",
                "delivered": "delivered",
                "cancelled": "failed",
            }

            mapped_status = status_map.get(new_status.lower(), "submitted")

            await pool.execute(
                """
                UPDATE subscription_shipments
                SET status = $1,
                    tracking_number = $2,
                    shipped_at = CASE WHEN $1 = 'shipped' THEN NOW() ELSE shipped_at END,
                    delivered_at = CASE WHEN $1 = 'delivered' THEN NOW() ELSE delivered_at END,
                    updated_at = NOW()
                WHERE id = $3
                """,
                mapped_status,
                status_result.get("shipments", [{}])[0].get("trackingNumber"),
                row["id"],
            )

            updates.append({
                "shipment_id": row["id"],
                "provider_order_id": row["print_provider_order_id"],
                "status": mapped_status,
            })

        return updates
