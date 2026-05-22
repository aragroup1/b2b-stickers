from typing import List
from app.core.stickers.config import StickerVariant, generate_variants


class VariantGenerator:
    """Generates sticker variant rows for a given product."""

    @staticmethod
    def create_variants(product_id: int) -> List[StickerVariant]:
        return generate_variants(product_id)
