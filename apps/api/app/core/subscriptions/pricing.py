from app.config import settings
from app.core.stickers.config import get_recurring_price


def compute_recurring_amount(retail_price: float, discount_percent: int | None = None) -> float:
    """Central calculation for discounted recurring price."""
    if discount_percent is None:
        discount_percent = settings.SUBSCRIBE_AND_SAVE_DISCOUNT_PERCENT
    return get_recurring_price(retail_price, discount_percent)


def get_or_create_recurring_price(variant) -> str:
    """Returns a Stripe Price ID for the given variant.

    Expects variant to have `.retail_price`, `.id`, `.sku`.
    """
    from app.core.subscriptions.stripe_client import StripeClient

    recurring = compute_recurring_amount(variant.retail_price)
    unit_amount_pence = int(round(recurring * 100))
    price = StripeClient.get_or_create_price(
        variant_id=variant.id,
        sku=variant.sku,
        unit_amount_pence=unit_amount_pence,
    )
    return price.id
