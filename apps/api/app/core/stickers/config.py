from dataclasses import dataclass
from typing import List

# Simplified variant matrix: sizes × pack quantities only
# Materials and shapes are now product-level attributes, not variants

SIZES_INCHES = [2.0, 3.0, 4.0, 5.0]

PACK_QUANTITIES = [10, 25, 50, 100, 250]

# Base retail pricing by size + pack (vinyl material as baseline)
# Shape and material are now standard (die-cut vinyl)
RETAIL_PRICES = {
    2.0: {10: 3.99, 25: 7.49, 50: 12.99, 100: 22.99, 250: 49.99},
    3.0: {10: 4.99, 25: 9.99, 50: 16.99, 100: 29.99, 250: 64.99},
    4.0: {10: 5.99, 25: 11.99, 50: 19.99, 100: 34.99, 250: 74.99},
    5.0: {10: 6.99, 25: 13.99, 50: 22.99, 100: 39.99, 250: 84.99},
}

# Unit cost estimates (for margin calculation)
UNIT_COSTS = {
    2.0: {10: 1.50, 25: 2.80, 50: 4.50, 100: 7.50, 250: 15.00},
    3.0: {10: 1.80, 25: 3.50, 50: 5.80, 100: 9.50, 250: 19.00},
    4.0: {10: 2.20, 25: 4.20, 50: 7.00, 100: 11.50, 250: 23.00},
    5.0: {10: 2.60, 25: 5.00, 50: 8.20, 100: 13.50, 250: 27.00},
}


@dataclass
class StickerVariant:
    size_inches: float
    pack_quantity: int
    unit_cost: float
    retail_price: float
    sku: str


def generate_variants(product_id: int) -> List[StickerVariant]:
    """Generate sticker variants for a product (size × pack only)."""
    variants = []
    for size in SIZES_INCHES:
        for pack in PACK_QUANTITIES:
            retail = RETAIL_PRICES[size][pack]
            cost = UNIT_COSTS[size][pack]
            sku = f"STK-{product_id:05d}-{int(size*10):02d}-{pack:03d}"
            variants.append(
                StickerVariant(
                    size_inches=size,
                    pack_quantity=pack,
                    unit_cost=cost,
                    retail_price=retail,
                    sku=sku,
                )
            )
    return variants


def get_recurring_price(retail_price: float, discount_percent: int = 10) -> float:
    """Compute discounted recurring subscription price."""
    return round(retail_price * (1 - discount_percent / 100), 2)


def compute_vat_inclusive_price(price_ex_vat: float, vat_rate_percent: float = 20.0) -> float:
    """Add VAT to a price."""
    return round(price_ex_vat * (1 + vat_rate_percent / 100), 2)


def compute_vat_amount(price_ex_vat: float, vat_rate_percent: float = 20.0) -> float:
    """Compute VAT amount from ex-VAT price."""
    return round(price_ex_vat * (vat_rate_percent / 100), 2)
