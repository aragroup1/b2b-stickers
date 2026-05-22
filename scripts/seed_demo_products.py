#!/usr/bin/env python3
"""
Seed demo products for development/testing without AI generation.

Creates sample products with placeholder artwork URLs for testing the storefront.
Usage:
    python scripts/seed_demo_products.py --count 20
"""

import asyncio
import argparse
import asyncpg
import os
import random

DSN = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/b2b_stickers")

DEMO_KEYWORDS = [
    ("craft beer labels", 1),
    ("coffee roaster stickers", 2),
    ("bakery packaging labels", 3),
    ("hot sauce labels", 4),
    ("candle warning labels", 5),
    ("handmade soap labels", 6),
    ("skincare product labels", 7),
    ("shampoo bar labels", 8),
    ("plant pot labels", 9),
    ("seed packet stickers", 11),
    ("jewellery box stickers", 12),
    ("clothing brand stickers", 13),
    ("tote bag stickers", 14),
    ("dog treat labels", 15),
    ("organic pet food stickers", 15),
    ("laptop decal stickers", 17),
    ("phone case labels", 18),
    ("thank you stickers", 19),
    ("planner stickers", 20),
    ("wedding favour labels", 24),
    ("protein powder labels", 26),
    ("fragile handle with care stickers", 28),
    ("handmade with love labels", 28),
    ("eco friendly packaging labels", 28),
]

STYLES = ["minimal_logo", "kawaii", "retro_badge", "hand_drawn", "cottagecore"]

# Placeholder image URLs (using picsum for demo)
PLACEHOLDER_IMAGES = [
    "https://picsum.photos/seed/sticker1/1024/1024",
    "https://picsum.photos/seed/sticker2/1024/1024",
    "https://picsum.photos/seed/sticker3/1024/1024",
    "https://picsum.photos/seed/sticker4/1024/1024",
    "https://picsum.photos/seed/sticker5/1024/1024",
]


async def seed_demo_products(count: int = 20):
    conn = await asyncpg.connect(DSN)

    try:
        # Ensure trends exist
        for kw, industry_id in DEMO_KEYWORDS[:count]:
            await conn.execute(
                """
                INSERT INTO trends (keyword, industry_id, region)
                VALUES ($1, $2, 'UK')
                ON CONFLICT (keyword) DO NOTHING
                """,
                kw, industry_id
            )

        # Get trend IDs
        trends = await conn.fetch(
            "SELECT id, keyword, industry_id FROM trends WHERE keyword = ANY($1)",
            [k for k, _ in DEMO_KEYWORDS[:count]]
        )

        generated = 0
        for trend in trends:
            style = random.choice(STYLES)
            image_url = random.choice(PLACEHOLDER_IMAGES)

            # Insert artwork
            artwork_id = await conn.fetchval(
                """
                INSERT INTO artwork (trend_id, prompt, negative_prompt, provider, model_used, style, image_url, generation_cost, quality_score, attributes)
                VALUES ($1, $2, $3, 'demo', 'demo', $4, $5, 0, 85, '{}')
                RETURNING id
                """,
                trend["id"],
                f"Demo sticker for {trend['keyword']}",
                "",
                style,
                image_url,
            )

            # Generate slug
            slug = f"{trend['keyword'].replace(' ', '-').replace('&', 'and')}-{artwork_id}"
            slug = "".join(c for c in slug if c.isalnum() or c == "-")

            # Insert product
            product_id = await conn.fetchval(
                """
                INSERT INTO products (artwork_id, industry_id, slug, title, description, tags, status, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, 'approved', $7)
                RETURNING id
                """,
                artwork_id,
                trend["industry_id"],
                slug,
                f"{trend['keyword'].title()} Stickers",
                f"Premium {trend['keyword']} stickers for your small business. Printed on high-quality vinyl in the UK.",
                [trend["keyword"], "stickers", "uk made", "small business", style],
                {"mockup_urls": [], "style": style},
            )

            # Generate variants
            sizes = [2.0, 3.0, 4.0, 5.0]
            packs = [10, 25, 50, 100, 250]
            prices = {
                2.0: {10: 3.99, 25: 7.49, 50: 12.99, 100: 22.99, 250: 49.99},
                3.0: {10: 4.99, 25: 9.99, 50: 16.99, 100: 29.99, 250: 64.99},
                4.0: {10: 5.99, 25: 11.99, 50: 19.99, 100: 34.99, 250: 74.99},
                5.0: {10: 6.99, 25: 13.99, 50: 22.99, 100: 39.99, 250: 84.99},
            }

            for size in sizes:
                for pack in packs:
                    await conn.execute(
                        """
                        INSERT INTO sticker_variants (product_id, size_inches, pack_quantity, unit_cost, retail_price, sku)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                        product_id,
                        size,
                        pack,
                        round(prices[size][pack] * 0.4, 2),
                        prices[size][pack],
                        f"STK-{product_id:05d}-{int(size*10):02d}-{pack:03d}",
                    )

            generated += 1
            print(f"Created product {product_id}: {trend['keyword']} ({style})")

        print(f"\n{'='*50}")
        print(f"Seeded {generated} demo products")
        print(f"{'='*50}")

    finally:
        await conn.close()


def main():
    parser = argparse.ArgumentParser(description="Seed demo products for testing")
    parser.add_argument("--count", type=int, default=20, help="Number of products to create")
    args = parser.parse_args()

    print("B2B Stickers — Demo Product Seeder")
    print(f"Creating {args.count} demo products...")
    print("-" * 50)

    asyncio.run(seed_demo_products(args.count))


if __name__ == "__main__":
    main()
