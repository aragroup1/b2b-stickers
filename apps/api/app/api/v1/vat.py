from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.dependencies import get_db
from app.config import settings
from app.core.stickers.config import compute_vat_inclusive_price, compute_vat_amount

router = APIRouter(prefix="/vat", tags=["vat"])


class VATCalculationRequest(BaseModel):
    price_ex_vat: float


class VATCalculationResponse(BaseModel):
    price_ex_vat: float
    vat_rate_percent: float
    vat_amount: float
    price_inc_vat: float


@router.post("/calculate", response_model=VATCalculationResponse)
async def calculate_vat(req: VATCalculationRequest):
    """Calculate VAT for a given ex-VAT price."""
    vat_amount = compute_vat_amount(req.price_ex_vat, settings.VAT_RATE_PERCENT)
    price_inc_vat = compute_vat_inclusive_price(req.price_ex_vat, settings.VAT_RATE_PERCENT)

    return VATCalculationResponse(
        price_ex_vat=req.price_ex_vat,
        vat_rate_percent=settings.VAT_RATE_PERCENT,
        vat_amount=vat_amount,
        price_inc_vat=price_inc_vat,
    )


@router.get("/config")
async def vat_config():
    """Get current VAT configuration."""
    return {
        "vat_rate_percent": settings.VAT_RATE_PERCENT,
        "vat_number": settings.VAT_NUMBER or None,
        "country": "GB",
    }


@router.post("/invoice")
async def generate_invoice(
    order_id: int,
    db=Depends(get_db),
):
    """Generate a VAT invoice for an order."""
    order = await db.fetchrow(
        """
        SELECT o.*, c.email, c.name, c.company_name, c.shipping_address
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.id = $1
        """,
        order_id,
    )

    if not order:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Order not found")

    order_value = float(order["order_value"] or 0)
    vat_amount = compute_vat_amount(order_value, settings.VAT_RATE_PERCENT)
    total = compute_vat_inclusive_price(order_value, settings.VAT_RATE_PERCENT)

    invoice = {
        "invoice_number": f"INV-{order_id:06d}",
        "date": order["created_at"].isoformat() if order["created_at"] else None,
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

    return invoice
