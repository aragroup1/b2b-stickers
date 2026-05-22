#!/usr/bin/env python3
"""
Product Generation Script for B2B Stickers

Generates AI sticker designs from trend keywords and creates products with variants.
Usage:
    python scripts/generate_products.py --trends "brewery labels,coffee stickers" --styles "brewery_emblem,retro_badge" --count 3
    python scripts/generate_products.py --all-trends --styles "minimal_logo,kawaii" --count 5
"""

import asyncio
import argparse
import asyncpg
import os
import sys

# Add the API app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "api"))

from app.config import settings
from app.services.product_generation import ProductGenerationService
from app.database import init_pool, close_pool


async def get_trends(pool: asyncpg.Pool, specific: list[str] | None = None) -> list[dict]:
    """Fetch trends from database."""
    if specific:
        rows = await pool.fetch(
            "SELECT * FROM trends WHERE keyword = ANY($1)",
            specific
        )
    else:
        rows = await pool.fetch(
            "SELECT * FROM trends WHERE designs_generated < designs_allocated OR designs_allocated = 0 ORDER BY created_at DESC LIMIT 50"
        )
    return [dict(r) for r in rows]


async def generate_products(
    trend_keywords: list[str] | None = None,
    styles: list[str] | None = None,
    designs_per_combo: int = 3,
    mode: str = "production",
):
    """Generate products from trends."""
    await init_pool()
    pool = await asyncpg.create_pool(
        settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    )

    try:
        # Get trends
        trends = await get_trends(pool, trend_keywords)
        if not trends:
            print("No trends found matching criteria.")
            return

        print(f"Found {len(trends)} trends to process")

        # Default styles if not specified
        if not styles:
            styles = [
                "minimal_logo",
                "kawaii",
                "retro_badge",
                "hand_drawn",
                "cottagecore",
            ]

        svc = ProductGenerationService()
        total_generated = 0

        for trend in trends:
            print(f"\nProcessing trend: {trend['keyword']} (ID: {trend['id']})")
            try:
                product_ids = await svc.generate_from_trend(
                    trend_id=trend["id"],
                    styles=styles,
                    designs_per_combo=designs_per_combo,
                    mode=mode,
                )
                total_generated += len(product_ids)

                # Update trend stats
                await pool.execute(
                    """
                    UPDATE trends
                    SET designs_generated = designs_generated + $1,
                        last_generated_at = NOW()
                    WHERE id = $2
                    """,
                    len(product_ids), trend["id"]
                )

                print(f"  Generated {len(product_ids)} products: {product_ids}")

            except Exception as e:
                print(f"  ERROR: {e}")
                continue

        print(f"\n{'='*50}")
        print(f"Total products generated: {total_generated}")
        print(f"{'='*50}")

    finally:
        await pool.close()
        await close_pool()


def main():
    parser = argparse.ArgumentParser(description="Generate sticker products from trends")
    parser.add_argument("--trends", type=str, help="Comma-separated trend keywords")
    parser.add_argument("--all-trends", action="store_true", help="Process all available trends")
    parser.add_argument("--styles", type=str, default="minimal_logo,kawaii,retro_badge",
                        help="Comma-separated styles (default: minimal_logo,kawaii,retro_badge)")
    parser.add_argument("--count", type=int, default=3,
                        help="Designs per style combo (default: 3)")
    parser.add_argument("--mode", type=str, default="production",
                        choices=["production", "testing"],
                        help="Generation mode (default: production)")

    args = parser.parse_args()

    trend_keywords = None
    if args.trends:
        trend_keywords = [k.strip() for k in args.trends.split(",")]
    elif not args.all_trends:
        print("Error: Specify --trends or --all-trends")
        parser.print_help()
        return

    styles = [s.strip() for s in args.styles.split(",")]

    print("B2B Stickers — Product Generation")
    print(f"Mode: {args.mode}")
    print(f"Styles: {styles}")
    print(f"Designs per combo: {args.count}")
    if trend_keywords:
        print(f"Trends: {trend_keywords}")
    else:
        print("Trends: ALL")
    print("-" * 50)

    asyncio.run(generate_products(
        trend_keywords=trend_keywords,
        styles=styles,
        designs_per_combo=args.count,
        mode=args.mode,
    ))


if __name__ == "__main__":
    main()
