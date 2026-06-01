#!/usr/bin/env python3
"""Seed realistic search volume data for trends based on keyword research estimates."""
import asyncio
import os
import asyncpg

# Realistic UK monthly search volume estimates for sticker/label keywords
KEYWORD_VOLUMES = {
    "craft beer labels": 5400,
    "coffee roaster stickers": 3200,
    "bakery packaging labels": 8100,
    "hot sauce labels": 4400,
    "candle warning labels": 2900,
    "honey jar labels": 6600,
    "soap packaging stickers": 3800,
    "artisan food labels": 1200,
    "juice bottle labels": 2100,
    "tea packaging labels": 2800,
    "vegan product stickers": 1900,
    "organic certification labels": 1500,
    "gluten free stickers": 3400,
    "handmade product labels": 2600,
    "farm shop stickers": 1800,
    "dog treat labels": 7200,
    "organic pet food stickers": 2100,
    "laptop decal stickers": 9400,
    "phone case labels": 5800,
    "thank you stickers": 12100,
    "planner stickers": 15600,
    "wedding favour labels": 8900,
}

KEYWORD_CATEGORIES = {
    "craft beer labels": "Food & Drink",
    "coffee roaster stickers": "Food & Drink",
    "bakery packaging labels": "Food & Drink",
    "hot sauce labels": "Food & Drink",
    "honey jar labels": "Food & Drink",
    "juice bottle labels": "Food & Drink",
    "tea packaging labels": "Food & Drink",
    "artisan food labels": "Food & Drink",
    "dog treat labels": "Pet Products",
    "organic pet food stickers": "Pet Products",
    "laptop decal stickers": "Tech Accessories",
    "phone case labels": "Tech Accessories",
    "candle warning labels": "Home & Garden",
    "soap packaging stickers": "Home & Garden",
    "thank you stickers": "Stationery & Events",
    "planner stickers": "Stationery & Events",
    "wedding favour labels": "Stationery & Events",
    "handmade product labels": "Craft & Handmade",
    "vegan product stickers": "Health & Wellness",
    "gluten free stickers": "Health & Wellness",
    "organic certification labels": "Health & Wellness",
    "farm shop stickers": "Retail & Shop",
}


async def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set")
        return

    conn = await asyncpg.connect(database_url)

    updated = 0
    for keyword, volume in KEYWORD_VOLUMES.items():
        category = KEYWORD_CATEGORIES.get(keyword)
        trend_score = min(100, round((volume / 150) + (volume / 1000) * 5))

        result = await conn.execute(
            """
            UPDATE trends
            SET search_volume = $1,
                trend_score = $2,
                category = COALESCE(category, $3),
                designs_allocated = COALESCE(designs_allocated, 5)
            WHERE keyword = $4
            """,
            volume, trend_score, category, keyword
        )
        if result != "UPDATE 0":
            updated += 1
            print(f"Updated: {keyword} → volume={volume}, score={trend_score}, category={category}")

    # Show summary
    rows = await conn.fetch("""
        SELECT category,
               COUNT(*) as count,
               SUM(search_volume) as total_volume,
               AVG(trend_score) as avg_score
        FROM trends
        WHERE search_volume IS NOT NULL
        GROUP BY category
        ORDER BY total_volume DESC
    """)

    print("\n=== SEO Demand Summary ===")
    for row in rows:
        print(f"{row['category']}: {row['count']} trends, {row['total_volume']:,.0f} total volume, avg score {row['avg_score']:.1f}")

    total = await conn.fetchval("SELECT COUNT(*) FROM trends WHERE search_volume IS NOT NULL")
    print(f"\nTotal trends with search volume: {total}")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
