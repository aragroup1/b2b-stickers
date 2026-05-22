from typing import List

from loguru import logger

from app.core.ai.generator import AIGenerator
from app.core.stickers.variants import VariantGenerator
from app.core.stickers.mockup_compositor import MockupCompositor
from app.core.listings.content_builder import ListingContentBuilder
from app.database import get_pool


class ProductGenerationService:
    """End-to-end product creation from trend to approved product with variants."""

    def __init__(self):
        self.ai = AIGenerator()
        self.mockups = MockupCompositor()
        self.content = ListingContentBuilder()

    async def generate_from_trend(
        self,
        trend_id: int,
        styles: List[str],
        designs_per_combo: int = 3,
        mode: str = "production",
    ) -> List[int]:
        pool = await get_pool()
        trend = await pool.fetchrow("SELECT * FROM trends WHERE id = $1", trend_id)
        if not trend:
            raise ValueError(f"Trend {trend_id} not found")

        product_ids = []
        for style in styles:
            for _ in range(designs_per_combo):
                result = await self.ai.generate(trend["keyword"], style, mode)

                # Skip if generation failed
                if "error" in result:
                    logger.error(f"Generation failed for {trend['keyword']}/{style}: {result['error']}")
                    continue

                # Insert artwork
                artwork_id = await pool.fetchval(
                    """
                    INSERT INTO artwork (trend_id, prompt, negative_prompt, provider, model_used, style, image_url, generation_cost, quality_score, attributes)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    RETURNING id
                    """,
                    trend_id,
                    result["prompt"],
                    result["negative_prompt"],
                    "replicate",
                    result["model_used"],
                    style,
                    result["image_url"],
                    result["generation_cost"],
                    result["quality_score"],
                    result["attributes"],
                )

                # Generate mockups (async but don't block on failure)
                mockup_urls = []
                try:
                    mockup_paths = await self.mockups.generate_mockups(result["image_url"])
                    mockup_urls = mockup_paths
                except Exception as e:
                    logger.warning(f"Mockup generation failed: {e}")

                # Insert product (pending_approval)
                product_id = await pool.fetchval(
                    """
                    INSERT INTO products (artwork_id, industry_id, slug, title, description, tags, status, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, 'pending_approval', $7)
                    RETURNING id
                    """,
                    artwork_id,
                    trend["industry_id"],
                    f"pending-{artwork_id}",
                    f"{trend['keyword'].title()} Stickers",
                    "",
                    [],
                    {"mockup_urls": mockup_urls},
                )

                # Generate variants (simplified: size × pack only)
                variants = VariantGenerator.create_variants(product_id)
                for v in variants:
                    await pool.execute(
                        """
                        INSERT INTO sticker_variants (product_id, size_inches, pack_quantity, unit_cost, retail_price, sku)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                        product_id,
                        v.size_inches,
                        v.pack_quantity,
                        v.unit_cost,
                        v.retail_price,
                        v.sku,
                    )

                product_ids.append(product_id)
                logger.info(f"Generated product {product_id} for trend {trend_id} style {style}")

        return product_ids
