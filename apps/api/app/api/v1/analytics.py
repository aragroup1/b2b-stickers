from fastapi import APIRouter, Depends
from datetime import date, timedelta

from app.dependencies import get_db
from app.core.auth import require_admin
from app.utils.cache import cache_get, cache_set

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
async def dashboard_analytics(db=Depends(get_db), _=Depends(require_admin)):
    cache_key = "analytics:dashboard"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    today = date.today()
    start_of_month = today.replace(day=1)

    # Total products
    total_products = await db.fetchval("SELECT COUNT(*) FROM products")
    approved_products = await db.fetchval("SELECT COUNT(*) FROM products WHERE status = 'approved'")
    active_products = await db.fetchval("SELECT COUNT(*) FROM products WHERE status = 'active'")

    # Total trends
    total_trends = await db.fetchval("SELECT COUNT(*) FROM trends")

    # Subscriptions
    active_subs = await db.fetchval("SELECT COUNT(*) FROM subscriptions WHERE status = 'active'")
    mrr = await db.fetchval(
        "SELECT COALESCE(SUM(recurring_amount), 0) FROM subscriptions WHERE status = 'active'"
    ) or 0

    # Orders this month
    monthly_orders = await db.fetchval(
        """
        SELECT COUNT(*) FROM orders
        WHERE created_at >= $1
        """,
        start_of_month,
    )

    monthly_revenue = await db.fetchval(
        """
        SELECT COALESCE(SUM(order_value), 0) FROM orders
        WHERE created_at >= $1
        """,
        start_of_month,
    ) or 0

    result = {
        "products": {
            "total": total_products,
            "approved": approved_products,
            "active": active_products,
        },
        "trends": {"total": total_trends},
        "subscriptions": {
            "active": active_subs,
            "mrr": round(float(mrr), 2),
        },
        "orders": {
            "this_month": monthly_orders,
            "revenue_this_month": round(float(monthly_revenue), 2),
        },
    }
    await cache_set(cache_key, result, ttl=60)
    return result


@router.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": date.today().isoformat()}
