from typing import List

# Material/shape removed from variants - now product-level attributes
MATERIAL_PRETTY = {
    "vinyl": "Premium Vinyl",
}


class ListingContentBuilder:
    """Auto-generates titles, descriptions, and tags for marketplace listings."""

    @staticmethod
    def build_title(theme: str, material: str, pack_qty: int, channel: str = "generic") -> str:
        material_pretty = MATERIAL_PRETTY.get(material, material.title())
        base = f"{theme} Stickers | {material_pretty} | Pack of {pack_qty} | UK Made"
        if channel == "amazon":
            return base[:200]
        if channel == "ebay":
            return base[:80]
        return base

    @staticmethod
    def build_description(product_title: str, channel: str = "generic") -> str:
        # TODO: integrate OpenAI gpt-4o-mini for per-channel rich descriptions
        bullets = [
            "Premium quality stickers printed in the UK",
            "Weatherproof and durable — suitable for indoor and outdoor use",
            "Perfect for small businesses, Etsy sellers, and product packaging",
            "Easy peel-and-stick application",
            "Shipped in protective packaging to prevent damage",
        ]
        bullet_text = "\n".join("• " + b for b in bullets)
        description = f"""{product_title}

{bullet_text}

Add a professional touch to your products with these high-quality stickers.
Designed for UK small businesses, breweries, candle makers, and more.
"""
        return description

    @staticmethod
    def build_tags(industry_slug: str, theme: str) -> List[str]:
        # TODO: pull from per-industry keyword pool
        base = [
            "stickers",
            "labels",
            "packaging",
            "small business",
            "uk made",
            "custom stickers",
            "product labels",
            "branding",
            "handmade",
            "etsy supplies",
            industry_slug.replace("-", " "),
            theme.lower(),
        ]
        return base[:13]
