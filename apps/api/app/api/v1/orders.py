from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from datetime import datetime

from app.dependencies import get_db
from app.config import settings
from app.core.auth import require_admin
from app.core.stickers.config import compute_vat_inclusive_price, compute_vat_amount
from app.core.print_provider import get_print_provider
from app.services.email import EmailService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
async def list_orders(
    source: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    _=Depends(require_admin),
):
    where_clauses = ["1=1"]
    params: list = []
    param_idx = 1

    if source:
        where_clauses.append(f"source = ${param_idx}")
        params.append(source)
        param_idx += 1
    if status:
        where_clauses.append(f"fulfillment_status = ${param_idx}")
        params.append(status)
        param_idx += 1

    where_sql = " AND ".join(where_clauses)

    rows = await db.fetch(
        f"""
        SELECT o.*, p.title as product_title, c.email as customer_email
        FROM orders o
        LEFT JOIN products p ON o.product_id = p.id
        LEFT JOIN customers c ON o.customer_id = c.id
        WHERE {where_sql}
        ORDER BY o.created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """,
        *params, limit, offset
    )

    return {"orders": [dict(r) for r in rows], "limit": limit, "offset": offset}


@router.get("/{order_id}")
async def get_order(order_id: int, db=Depends(get_db), _=Depends(require_admin)):
    row = await db.fetchrow(
        """
        SELECT o.*, p.title as product_title, c.email as customer_email,
               c.name as customer_name, c.company_name
        FROM orders o
        LEFT JOIN products p ON o.product_id = p.id
        LEFT JOIN customers c ON o.customer_id = c.id
        WHERE o.id = $1
        """,
        order_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    return dict(row)


@router.post("/{order_id}/fulfill")
async def fulfill_order(order_id: int, db=Depends(get_db), _=Depends(require_admin)):
    """Submit an order to the print provider for fulfillment."""
    order = await db.fetchrow(
        """
        SELECT o.*, p.title as product_title, a.image_url,
               c.email, c.name, c.shipping_address,
               sv.size_inches, sv.pack_quantity, sv.sku
        FROM orders o
        LEFT JOIN products p ON o.product_id = p.id
        LEFT JOIN artwork a ON p.artwork_id = a.id
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN sticker_variants sv ON o.variant_id = sv.id
        WHERE o.id = $1
        """,
        order_id,
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order["fulfillment_status"] not in ("pending", "processing"):
        raise HTTPException(status_code=400, detail=f"Order already {order['fulfillment_status']}")

    # Get print provider
    provider = get_print_provider()

    # Build shipping dict
    shipping = order["shipping_address"] or {}
    if not shipping.get("line1"):
        raise HTTPException(status_code=400, detail="No shipping address on order")

    # Submit to print provider
    result = await provider.submit_order(
        order_id=order_id,
        artwork_url=order["image_url"] or "",
        shipping=shipping,
        variant={
            "id": order["variant_id"],
            "size_inches": order["size_inches"],
            "pack_quantity": order["pack_quantity"],
        },
        quantity=1,
    )

    if result.get("success"):
        # Update order with provider details
        await db.execute(
            """
            UPDATE orders
            SET fulfillment_status = 'processing',
                fulfillment_provider = 'prodigi',
                external_order_id = $1,
                updated_at = NOW()
            WHERE id = $2
            """,
            result["provider_order_id"], order_id,
        )

        # If subscription shipment, update that too
        if order["subscription_shipment_id"]:
            await db.execute(
                """
                UPDATE subscription_shipments
                SET status = 'submitted',
                    print_provider_order_id = $1,
                    updated_at = NOW()
                WHERE id = $2
                """,
                result["provider_order_id"], order["subscription_shipment_id"],
            )

        return {
            "status": "submitted",
            "provider_order_id": result["provider_order_id"],
            "cost": result.get("cost"),
        }
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "Fulfillment failed"))


@router.post("/{order_id}/invoice")
async def generate_order_invoice(order_id: int, db=Depends(get_db)):
    """Generate and store invoice for an order."""
    order = await db.fetchrow(
        """
        SELECT o.*, c.email, c.name, c.company_name, c.shipping_address, c.vat_number
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.id = $1
        """,
        order_id,
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_value = float(order["order_value"] or 0)
    vat_amount = compute_vat_amount(order_value, settings.VAT_RATE_PERCENT)
    total = compute_vat_inclusive_price(order_value, settings.VAT_RATE_PERCENT)

    invoice_number = f"INV-{order_id:06d}-{datetime.now().strftime('%Y%m%d')}"

    await db.execute(
        """
        UPDATE orders
        SET invoice_number = $1, invoice_generated_at = NOW(),
            vat_amount = $2, order_total = $3
        WHERE id = $4
        """,
        invoice_number, vat_amount, total, order_id,
    )

    return {
        "invoice_number": invoice_number,
        "date": datetime.now().isoformat(),
        "vat_number": settings.VAT_NUMBER or "Pending registration",
        "seller": {
            "name": "B2B Stickers Ltd",
            "address": "United Kingdom",
            "vat_number": settings.VAT_NUMBER,
        },
        "customer": {
            "name": order["name"] or order["email"],
            "company": order["company_name"],
            "email": order["email"],
            "vat_number": order["vat_number"],
            "shipping_address": order["shipping_address"],
        },
        "line_items": [
            {
                "description": f"Order #{order_id}",
                "quantity": 1,
                "unit_price_ex_vat": order_value,
                "vat_rate": settings.VAT_RATE_PERCENT,
                "vat_amount": vat_amount,
                "total_inc_vat": total,
            }
        ],
        "subtotal_ex_vat": order_value,
        "vat_amount": vat_amount,
        "total_inc_vat": total,
    }


@router.post("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    tracking_number: Optional[str] = None,
    db=Depends(get_db),
):
    """Update order status and optionally add tracking."""
    valid_statuses = ['pending','processing','fulfilled','shipped','delivered','cancelled','refunded']
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    await db.execute(
        """
        UPDATE orders
        SET fulfillment_status = $1,
            tracking_number = COALESCE($2, tracking_number),
            updated_at = NOW()
        WHERE id = $3
        """,
        status, tracking_number, order_id,
    )

    # Send shipping notification if status is 'shipped'
    if status == 'shipped':
        customer = await db.fetchrow(
            "SELECT c.email FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.id = $1",
            order_id,
        )
        if customer:
            await EmailService.send_shipping_notification(customer["email"], tracking_number)

    return {"status": "updated", "order_id": order_id, "new_status": status}


@router.post("/sync")
async def sync_orders(db=Depends(get_db), _=Depends(require_admin)):
    from app.workers.tasks import sync_amazon_orders, sync_ebay_orders
    amazon_result = sync_amazon_orders.delay()
    ebay_result = sync_ebay_orders.delay()
    return {"synced": {"amazon": amazon_result.id, "ebay": ebay_result.id}}
