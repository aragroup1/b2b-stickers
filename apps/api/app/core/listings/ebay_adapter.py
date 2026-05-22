from abc import ABC
from typing import Optional

from app.config import settings


class EbayAdapter(ABC):
    """eBay UK Sell APIs adapter."""

    MARKETPLACE_ID = "EBAY_GB"
    CATEGORY_ID = "159005"  # Stickers / UK — confirm at runtime

    async def create_inventory_item(
        self,
        sku: str,
        title: str,
        description: str,
        images: list[str],
        price: float,
        quantity: int = 999,
    ) -> dict:
        # TODO: implement eBay Inventory API + Offer API
        return {"marketplace_id": self.MARKETPLACE_ID, "sku": sku, "status": "stub"}

    async def create_offer(self, sku: str, price: float, quantity: int) -> dict:
        return {"sku": sku, "price": price, "status": "stub"}

    async def get_orders(self, since: Optional[str] = None) -> list[dict]:
        return []
