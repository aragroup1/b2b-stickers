from abc import ABC, abstractmethod
from typing import Optional

from app.config import settings


class AmazonAdapter(ABC):
    """Amazon UK SP-API adapter."""

    MARKETPLACE_ID = "A1F83G8C2ARO7P"
    PRODUCT_TYPE = "STATIONERY_AND_CRAFT_SUPPLIES"

    async def create_listing(
        self,
        sku: str,
        title: str,
        description: str,
        bullet_points: list[str],
        images: list[str],
        price: float,
        quantity: int = 999,
    ) -> dict:
        # TODO: implement SP-API Listings Items API call
        return {"marketplace_id": self.MARKETPLACE_ID, "sku": sku, "status": "stub"}

    async def update_inventory(self, sku: str, quantity: int) -> dict:
        return {"sku": sku, "quantity": quantity, "status": "stub"}

    async def get_orders(self, since: Optional[str] = None) -> list[dict]:
        return []
