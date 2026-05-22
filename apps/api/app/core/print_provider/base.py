from abc import ABC, abstractmethod
from typing import Optional


class PrintProvider(ABC):
    """Abstract base class for print-on-demand providers."""

    @abstractmethod
    async def quote(self, variant_id: int, quantity: int) -> dict:
        """Get a cost quote for printing an order."""
        pass

    @abstractmethod
    async def submit_order(
        self,
        order_id: int,
        artwork_url: str,
        shipping: dict,
        variant: dict,
        quantity: int = 1,
    ) -> dict:
        """Submit an order to the print provider for fulfillment."""
        pass

    @abstractmethod
    async def get_status(self, provider_order_id: str) -> dict:
        """Get the status of a submitted order."""
        pass

    @abstractmethod
    async def cancel(self, provider_order_id: str) -> bool:
        """Cancel an order if possible."""
        pass
