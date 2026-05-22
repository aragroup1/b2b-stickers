from loguru import logger

from app.core.print_provider.base import PrintProvider


class StubPrintProvider(PrintProvider):
    """Stub implementation that logs and returns fake tracking."""

    async def quote(self, variant_id: int, quantity: int) -> dict:
        logger.info(f"[Stub] quote for variant {variant_id} qty {quantity}")
        return {"variant_id": variant_id, "quantity": quantity, "cost": 1.50}

    async def submit_order(self, order_id: int, shipping: dict) -> dict:
        logger.info(f"[Stub] submit_order {order_id}")
        return {
            "order_id": order_id,
            "provider_order_id": f"STUB-{order_id:06d}",
            "tracking_number": f"TRACK{order_id:06d}",
            "status": "submitted",
        }

    async def get_status(self, provider_order_id: str) -> dict:
        logger.info(f"[Stub] get_status {provider_order_id}")
        return {"provider_order_id": provider_order_id, "status": "shipped"}

    async def cancel(self, provider_order_id: str) -> bool:
        logger.info(f"[Stub] cancel {provider_order_id}")
        return True
