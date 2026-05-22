"""
Prodigi Print Provider Integration

Prodigi is a UK-based print-on-demand API with competitive B2B pricing.
Free to sign up, pay only for what you print. No monthly fees.

API Docs: https://www.prodigi.com/print-api/
Pricing: ~£0.50-£2.00 per sticker sheet depending on size/quantity
Shipping: UK from ~£1.50 standard

Cost-effective for low-volume startup — only pay when you get an order.
"""

import httpx
from typing import Optional
from loguru import logger

from app.core.print_provider.base import PrintProvider
from app.config import settings


PRODIGI_API_BASE = "https://api.prodigi.com/v4"


class ProdigiPrintProvider(PrintProvider):
    """Prodigi API integration for sticker print-on-demand fulfillment."""

    def __init__(self):
        self.api_key = settings.PRODIGI_API_KEY or ""
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an authenticated request to Prodigi API."""
        if not self.api_key:
            raise RuntimeError("PRODIGI_API_KEY not configured")

        url = f"{PRODIGI_API_BASE}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(method, url, headers=self.headers, **kwargs)
            resp.raise_for_status()
            return resp.json()

    async def quote(self, variant_id: int, quantity: int) -> dict:
        """Get a shipping quote for an order.

        Prodigi doesn't have a separate quote endpoint — we estimate
        based on their published pricing tiers.
        """
        # Estimate costs based on variant + quantity
        # These are conservative estimates; real cost comes from order creation
        base_cost = 1.20  # Base print cost per item
        shipping = 1.99   # UK standard shipping

        total = (base_cost * quantity) + shipping

        return {
            "variant_id": variant_id,
            "quantity": quantity,
            "estimated_print_cost": round(base_cost * quantity, 2),
            "estimated_shipping": shipping,
            "estimated_total": round(total, 2),
            "currency": "GBP",
            "note": "Estimate — actual cost from order creation",
        }

    async def submit_order(
        self,
        order_id: int,
        artwork_url: str,
        shipping: dict,
        variant: dict,
        quantity: int = 1,
    ) -> dict:
        """Submit an order to Prodigi for printing and fulfillment.

        Args:
            order_id: Our internal order ID
            artwork_url: Public URL to the sticker artwork image
            shipping: Dict with name, address lines, city, postcode, country
            variant: Sticker variant dict with size_inches, pack_quantity
            quantity: Number of packs to order
        """
        size = variant.get("size_inches", 3.0)
        pack_qty = variant.get("pack_quantity", 10)

        # Map size to Prodigi SKU
        # Prodigi uses SKUs like "sticker-sheet-a4", "sticker-sheet-a5"
        # We map our sizes to their closest product
        if size <= 2.5:
            prodigi_sku = "sticker-sheet-a6"
        elif size <= 3.5:
            prodigi_sku = "sticker-sheet-a5"
        elif size <= 4.5:
            prodigi_sku = "sticker-sheet-a4"
        else:
            prodigi_sku = "sticker-sheet-a3"

        payload = {
            "shippingMethod": "Standard",
            "recipient": {
                "name": shipping.get("name", ""),
                "address": {
                    "line1": shipping.get("line1", ""),
                    "line2": shipping.get("line2", ""),
                    "townOrCity": shipping.get("city", ""),
                    "postalOrZipCode": shipping.get("postal_code", ""),
                    "countryCode": shipping.get("country", "GB"),
                    "stateOrCounty": shipping.get("state", ""),
                },
            },
            "items": [
                {
                    "sku": prodigi_sku,
                    "copies": quantity,
                    "sizing": "fillPrintArea",
                    "attributes": {
                        "wrap": "none",
                    },
                    "assets": [
                        {
                            "printArea": "default",
                            "url": artwork_url,
                        }
                    ],
                    "merchantReference": f"b2b-stickers-{order_id}",
                }
            ],
            "metadata": {
                "source": "b2b-stickers",
                "order_id": str(order_id),
                "variant_id": str(variant.get("id", "")),
                "pack_quantity": str(pack_qty),
            },
        }

        try:
            result = await self._request("POST", "/orders", json=payload)
            logger.info(f"Prodigi order submitted: {result.get('order', {}).get('id')}")

            return {
                "success": True,
                "provider_order_id": result.get("order", {}).get("id"),
                "status": result.get("order", {}).get("status"),
                "cost": result.get("order", {}).get("cost", {}),
                "tracking": result.get("order", {}).get("shipments", [{}])[0].get("carrier", {}),
                "raw": result,
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Prodigi order failed: {e.response.status_code} {e.response.text}")
            return {
                "success": False,
                "error": f"Prodigi API error: {e.response.status_code}",
                "details": e.response.text,
            }
        except Exception as e:
            logger.error(f"Prodigi order failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def get_status(self, provider_order_id: str) -> dict:
        """Get the status of a Prodigi order."""
        try:
            result = await self._request("GET", f"/orders/{provider_order_id}")
            order = result.get("order", {})

            return {
                "provider_order_id": provider_order_id,
                "status": order.get("status"),
                "status_details": order.get("status", {}).get("details", {}),
                "shipments": order.get("shipments", []),
                "cost": order.get("cost", {}),
                "raw": result,
            }
        except Exception as e:
            logger.error(f"Prodigi status check failed: {e}")
            return {
                "provider_order_id": provider_order_id,
                "status": "unknown",
                "error": str(e),
            }

    async def cancel(self, provider_order_id: str) -> bool:
        """Cancel an order if it hasn't started printing.

        Prodigi allows cancellation within a short window after submission.
        """
        try:
            result = await self._request("POST", f"/orders/{provider_order_id}/actions/cancel")
            success = result.get("outcome", {}).get("status") == "Cancelled"
            logger.info(f"Prodigi cancel {provider_order_id}: {success}")
            return success
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                logger.warning(f"Prodigi order {provider_order_id} cannot be cancelled — already in production")
                return False
            logger.error(f"Prodigi cancel failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Prodigi cancel failed: {e}")
            return False


class ProdigiMockProvider(PrintProvider):
    """Mock Prodigi provider for development — logs instead of calling API.

    Use this when PRODIGI_API_KEY is not set. It simulates the full flow
    without spending money or creating real orders.
    """

    async def quote(self, variant_id: int, quantity: int) -> dict:
        logger.info(f"[MOCK Prodigi] quote for variant {variant_id} qty {quantity}")
        return {
            "variant_id": variant_id,
            "quantity": quantity,
            "estimated_print_cost": 1.20 * quantity,
            "estimated_shipping": 1.99,
            "estimated_total": round(1.20 * quantity + 1.99, 2),
            "currency": "GBP",
            "note": "MOCK — no real order created",
        }

    async def submit_order(self, order_id: int, artwork_url: str, shipping: dict, variant: dict, quantity: int = 1) -> dict:
        logger.info(f"[MOCK Prodigi] submit_order {order_id} for {artwork_url}")
        import uuid
        return {
            "success": True,
            "provider_order_id": f"MOCK-{uuid.uuid4().hex[:8].upper()}",
            "status": "created",
            "cost": {"total": 3.19},
            "tracking": {"carrier": "MockCarrier", "trackingNumber": f"MOCK{order_id:06d}"},
            "note": "MOCK order — no real print job created",
        }

    async def get_status(self, provider_order_id: str) -> dict:
        logger.info(f"[MOCK Prodigi] get_status {provider_order_id}")
        return {
            "provider_order_id": provider_order_id,
            "status": "shipped",
            "shipments": [{"carrier": "MockCarrier", "trackingNumber": f"TRACK{provider_order_id}"}],
        }

    async def cancel(self, provider_order_id: str) -> bool:
        logger.info(f"[MOCK Prodigi] cancel {provider_order_id}")
        return True


def get_print_provider() -> PrintProvider:
    """Factory: returns real Prodigi if API key set, otherwise mock."""
    if settings.PRODIGI_API_KEY:
        return ProdigiPrintProvider()
    return ProdigiMockProvider()
