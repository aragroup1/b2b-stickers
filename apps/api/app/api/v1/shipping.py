from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

from app.config import settings

router = APIRouter(prefix="/shipping", tags=["shipping"])

# UK shipping rates by order value
SHIPPING_RATES = {
    "standard": {
        "name": "Standard Delivery",
        "description": "3-5 business days",
        "tiers": [
            {"min": 0, "max": 14.99, "price": 3.49},
            {"min": 15.00, "max": 49.99, "price": 2.99},
            {"min": 50.00, "max": 999999, "price": 0.00},  # Free over £50
        ],
    },
    "express": {
        "name": "Express Delivery",
        "description": "1-2 business days",
        "tiers": [
            {"min": 0, "max": 999999, "price": 5.99},
        ],
    },
}


class ShippingQuoteRequest(BaseModel):
    postal_code: str
    order_value: float
    method: str = "standard"


@router.post("/quote")
async def get_shipping_quote(req: ShippingQuoteRequest):
    """Get shipping cost for a given order value and postcode."""
    method = SHIPPING_RATES.get(req.method)
    if not method:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Unknown shipping method: {req.method}")

    # Find applicable tier
    price = None
    for tier in method["tiers"]:
        if tier["min"] <= req.order_value <= tier["max"]:
            price = tier["price"]
            break

    if price is None:
        price = method["tiers"][-1]["price"]

    # VAT on shipping
    from app.core.stickers.config import compute_vat_amount
    vat_on_shipping = compute_vat_amount(price, settings.VAT_RATE_PERCENT)

    return {
        "postal_code": req.postal_code,
        "order_value": req.order_value,
        "method": req.method,
        "method_name": method["name"],
        "description": method["description"],
        "shipping_cost_ex_vat": price,
        "shipping_vat": vat_on_shipping,
        "shipping_cost_inc_vat": price + vat_on_shipping,
        "free_shipping_threshold": 50.00,
        "is_free": price == 0,
    }


@router.get("/methods")
async def list_shipping_methods():
    """List available shipping methods."""
    return {
        "methods": [
            {
                "id": key,
                "name": method["name"],
                "description": method["description"],
            }
            for key, method in SHIPPING_RATES.items()
        ]
    }
