import stripe
from loguru import logger

from app.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeClient:
    """Wraps stripe-python for subscriptions, checkout, and webhooks."""

    @staticmethod
    def create_customer(email: str, name: str | None = None, shipping: dict | None = None) -> stripe.Customer:
        return stripe.Customer.create(
            email=email,
            name=name,
            shipping=shipping,
        )

    @staticmethod
    def get_or_create_price(variant_id: int, sku: str, unit_amount_pence: int) -> stripe.Price:
        """Create a dynamic recurring Price for a variant, or return existing."""
        # TODO: cache price IDs by variant to avoid duplicates
        return stripe.Price.create(
            unit_amount=unit_amount_pence,
            currency="gbp",
            recurring={"interval": "month"},
            product=settings.STRIPE_SUBSCRIPTION_PRODUCT_ID,
            metadata={"variant_id": str(variant_id), "sku": sku},
        )

    @staticmethod
    def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict | None = None,
    ) -> stripe.checkout.Session:
        return stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {},
            subscription_data={"metadata": metadata or {}} if metadata else {},
        )

    @staticmethod
    def create_portal_session(customer_id: str, return_url: str) -> stripe.billing_portal.Session:
        return stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

    @staticmethod
    def construct_event(payload: bytes, sig_header: str) -> stripe.Event:
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
