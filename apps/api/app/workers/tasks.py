from celery import shared_task, chord, group
from loguru import logger
import asyncio
import json

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
            total = len(trend_ids) * len(styles) * designs_per_combo
            
            # Create or update job record
            pool = await get_pool()
            try:
                await pool.execute(
                    """INSERT INTO jobs (id, kind, status, params, progress, created_at, updated_at)
                       VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                       ON CONFLICT (id) DO UPDATE SET
                         status = EXCLUDED.status,
                         progress = EXCLUDED.progress,
                         updated_at = NOW()""",
                    self.request.id,
                    "generate_batch",
                    "running",
                    json.dumps({"trend_ids": trend_ids, "styles": styles, "designs_per_combo": designs_per_combo, "mode": mode}),
                    json.dumps({"completed": 0, "total": total}),
                )
            except Exception as e:
                logger.warning(f"Could not create job record: {e}")
            
            for tid in trend_ids:
                ids = await svc.generate_from_trend(tid, styles, designs_per_combo, mode)
                results.extend(ids)

                # Update job progress
                try:
                    await pool.execute(
                        "UPDATE jobs SET progress = $1, status = $2, updated_at = NOW() WHERE id = $3",
                        json.dumps({"completed": len(results), "total": total}),
                        "completed" if len(results) >= total else "running",
                        self.request.id,
                    )
                except Exception as e:
                    logger.warning(f"Could not update job progress: {e}")

            return {"generated": len(results), "product_ids": results}
        finally:
            await close_pool()

    return asyncio.run(_run())


@shared_task(bind=True)
def generate_for_trend(self, trend_id: int, styles: list[str], designs_per_combo: int, mode: str = "production", parent_job_id: str = ""):
    """Generate products for a single trend. Used as a sub-task in volume-weighted generation."""
    async def _run():
        await init_pool()
        try:
            svc = ProductGenerationService()
            pool = await get_pool()
            
            # Get trend info for logging
            trend = await pool.fetchrow("SELECT keyword, search_volume FROM trends WHERE id = $1", trend_id)
            keyword = trend["keyword"] if trend else f"trend-{trend_id}"
            
            logger.info(f"[VolumeWeighted] Generating for '{keyword}': {designs_per_combo} designs × {len(styles)} styles = {designs_per_combo * len(styles)} products")
            
            ids = await svc.generate_from_trend(trend_id, styles, designs_per_combo, mode)
            
            # Update trend counters
            await pool.execute(
                "UPDATE trends SET designs_generated = designs_generated + $1 WHERE id = $2",
                len(ids), trend_id
            )
            
            logger.info(f"[VolumeWeighted] Completed '{keyword}': {len(ids)} products generated")
            
            return {
                "trend_id": trend_id,
                "keyword": keyword,
                "generated": len(ids),
                "product_ids": ids,
            }
        finally:
            await close_pool()
    
    return asyncio.run(_run())


@shared_task(bind=True)
def refresh_trend_volumes(self, limit: int = 200):
    """Fill search_volume via Google Trends for trends lacking Keyword Planner data.

    Keyword Planner volumes (volume_source='keyword_planner') are never overwritten.
    """
    async def _run():
        await init_pool()
        try:
            pool = await get_pool()
            rows = await pool.fetch(
                "SELECT id, keyword FROM trends "
                "WHERE volume_source IS DISTINCT FROM 'keyword_planner' "
                "ORDER BY (search_volume IS NULL) DESC, id "
                "LIMIT $1",
                limit,
            )
            if not rows:
                return {"updated": 0, "eligible": 0}
            from app.services.keyword_volume import KeywordVolumeService, SCALE
            svc = KeywordVolumeService()
            interest = svc.fetch_interest([r["keyword"] for r in rows])
            updated, skipped = 0, 0
            for r in rows:
                score = interest.get(r["keyword"]) or 0
                if score <= 0:
                    # Google Trends has no usable signal for this (often long-tail B2B)
                    # term — never overwrite existing data with a meaningless 0.
                    skipped += 1
                    continue
                await pool.execute(
                    "UPDATE trends SET trend_interest = $1, search_volume = $2, "
                    "volume_source = 'google_trends' WHERE id = $3",
                    int(score), int(score * SCALE), r["id"],
                )
                updated += 1
            logger.info(f"refresh_trend_volumes: updated {updated}, skipped {skipped} (no Trends data)")
            return {"updated": updated, "skipped": skipped, "eligible": len(rows)}
        finally:
            await close_pool()

    return asyncio.run(_run())


@shared_task(bind=True)
def composite_product_mockups(self, product_id: int):
    """Generate lifestyle mockups for an approved product and store the URLs (Tier 1).

    Composites the sticker onto industry-relevant backdrops + a clean shot. No-ops
    gracefully if object storage isn't configured yet.
    """
    async def _run():
        await init_pool()
        try:
            pool = await get_pool()
            row = await pool.fetchrow(
                """
                SELECT p.id, p.metadata, a.image_url, i.name AS industry_name
                FROM products p
                JOIN artwork a ON p.artwork_id = a.id
                LEFT JOIN industries i ON p.industry_id = i.id
                WHERE p.id = $1
                """,
                product_id,
            )
            if not row or not row["image_url"]:
                return {"product_id": product_id, "mockups": 0, "skipped": "no image"}

            from app.core.stickers.mockup_compositor import MockupCompositor
            urls = await MockupCompositor().composite_and_store(row["image_url"], row["industry_name"])

            meta = {}
            if row["metadata"]:
                try:
                    meta = json.loads(row["metadata"])
                except (TypeError, ValueError):
                    meta = {}
            meta["mockup_urls"] = urls
            await pool.execute(
                "UPDATE products SET metadata = $1 WHERE id = $2", json.dumps(meta), product_id
            )
            logger.info(f"composite_product_mockups: {len(urls)} mockups for product {product_id}")
            return {"product_id": product_id, "mockups": len(urls)}
        finally:
            await close_pool()

    return asyncio.run(_run())


@shared_task(bind=True)
def generate_winner_lifestyle(self, product_id: int):
    """STUB (Tier 2): AI-generated lifestyle scenes for proven sellers.

    Activates post-launch when sales data exists (needs Stripe + orders). Currently
    a no-op placeholder so the trigger can be wired without firing.
    """
    logger.info(f"[stub] generate_winner_lifestyle({product_id}) — deferred until sales data exists")
    return {"product_id": product_id, "status": "deferred"}


@shared_task(bind=True)
def generate_volume_weighted(self, target_total: int = 1000, mode: str = "production"):
    """Generate products distributed by search volume across all trends.
    
    Calculates designs per trend proportionally, then queues individual
    trend generation tasks.
    """
    async def _run():
        await init_pool()
        try:
            pool = await get_pool()
            
            # Get all trends with search volume
            trends = await pool.fetch(
                "SELECT id, keyword, search_volume, designs_generated FROM trends WHERE search_volume IS NOT NULL ORDER BY search_volume DESC"
            )
            
            if not trends:
                return {"error": "No trends with search volume found"}
            
            total_volume = sum(t["search_volume"] or 0 for t in trends)
            
            # Calculate allocation per trend
            allocations = []
            for trend in trends:
                vol = trend["search_volume"] or 0
                # Proportional allocation, minimum 2 designs
                target_designs = max(2, round((vol / total_volume) * target_total))
                # Account for already generated
                remaining = max(0, target_designs - (trend["designs_generated"] or 0))
                allocations.append({
                    "id": trend["id"],
                    "keyword": trend["keyword"],
                    "volume": vol,
                    "target_designs": target_designs,
                    "already_generated": trend["designs_generated"] or 0,
                    "remaining": remaining,
                })
            
            # Adjust to hit exactly target_total
            current_total = sum(a["target_designs"] for a in allocations)
            if current_total != target_total:
                # Adjust largest trend to make up difference
                diff = target_total - current_total
                allocations[0]["target_designs"] += diff
                allocations[0]["remaining"] = max(0, allocations[0]["target_designs"] - allocations[0]["already_generated"])
            
            # Update designs_allocated
            for alloc in allocations:
                await pool.execute(
                    "UPDATE trends SET designs_allocated = $1 WHERE id = $2",
                    alloc["target_designs"], alloc["id"]
                )
            
            # Filter to trends that still need products
            needed = [a for a in allocations if a["remaining"] > 0]
            total_to_generate = sum(a["remaining"] for a in needed)
            
            # Create master job record
            try:
                await pool.execute(
                    """INSERT INTO jobs (id, kind, status, params, progress, created_at, updated_at)
                       VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                       ON CONFLICT (id) DO UPDATE SET
                         status = EXCLUDED.status,
                         params = EXCLUDED.params,
                         progress = EXCLUDED.progress,
                         updated_at = NOW()""",
                    str(self.request.id),
                    "volume_weighted",
                    "running",
                    json.dumps({
                        "target_total": target_total,
                        "mode": mode,
                        "trends_count": len(needed),
                        "total_to_generate": total_to_generate,
                        "allocations": [{"id": a["id"], "keyword": a["keyword"], "remaining": a["remaining"]} for a in needed],
                    }),
                    json.dumps({"completed": 0, "total": total_to_generate}),
                )
            except Exception as e:
                logger.warning(f"Could not create master job record: {e}")
            
            # All available styles
            all_styles = [
                "kawaii", "retro_badge", "minimal_logo", "hand_drawn",
                "brewery_emblem", "vintage_americana", "holographic_ready",
                "motivational_quote", "novelty_meme", "packaging_seal",
                "cottagecore", "y2k",
            ]
            
            generated_total = 0
            results = []
            
            # Process each trend sequentially (to avoid DB pool exhaustion)
            svc = ProductGenerationService()
            
            for alloc in needed:
                designs_per_combo = max(1, alloc["remaining"] // len(all_styles))
                extra = alloc["remaining"] % len(all_styles)
                
                # Distribute extra designs across first N styles
                styles_for_trend = all_styles[:]
                
                logger.info(f"[VolumeWeighted] Trend '{alloc['keyword']}': generating {alloc['remaining']} products")
                
                # Generate directly (not through Celery subtask to avoid nested asyncio.run)
                ids = await svc.generate_from_trend(
                    alloc["id"],
                    styles_for_trend,
                    designs_per_combo + (1 if extra > 0 else 0),
                    mode,
                )
                
                count = len(ids)
                generated_total += count
                results.append({
                    "trend_id": alloc["id"],
                    "keyword": alloc["keyword"],
                    "generated": count,
                    "product_ids": ids,
                })
                
                # Update trend counters
                await pool.execute(
                    "UPDATE trends SET designs_generated = designs_generated + $1 WHERE id = $2",
                    count, alloc["id"]
                )
                
                # Update master job progress
                try:
                    await pool.execute(
                        "UPDATE jobs SET progress = $1, updated_at = NOW() WHERE id = $2",
                        json.dumps({"completed": generated_total, "total": total_to_generate}),
                        str(self.request.id),
                    )
                except Exception as e:
                    logger.warning(f"Could not update master job: {e}")
            
            # Mark master job complete
            try:
                await pool.execute(
                    "UPDATE jobs SET status = $1, result = $2, updated_at = NOW() WHERE id = $3",
                    "completed",
                    json.dumps({"generated": generated_total, "trends": len(needed)}),
                    str(self.request.id),
                )
            except Exception as e:
                logger.warning(f"Could not complete master job: {e}")
            
            logger.info(f"[VolumeWeighted] COMPLETE: {generated_total} products across {len(needed)} trends")
            
            return {
                "generated": generated_total,
                "trends_processed": len(needed),
                "target_total": target_total,
                "allocations": allocations,
            }
        finally:
            await close_pool()
    
    return asyncio.run(_run())
