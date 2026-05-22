#!/usr/bin/env python3
"""Seed ~1,000 sticker keywords into the trends table."""

import asyncio
import asyncpg
import os

KEYWORDS = [
    # Food & Beverage
    ("craft beer label stickers", 1),
    ("brewery logo stickers", 1),
    ("coffee roaster labels", 2),
    ("artisan coffee stickers", 2),
    ("bakery packaging labels", 3),
    ("handmade bread stickers", 3),
    ("hot sauce labels", 4),
    ("chilli sauce stickers", 4),
    # Health & Beauty
    ("candle warning labels", 5),
    ("soy candle stickers", 5),
    ("handmade soap labels", 6),
    ("artisan soap stickers", 6),
    ("skincare product labels", 7),
    ("organic skincare stickers", 7),
    ("shampoo bar labels", 8),
    ("hair oil stickers", 8),
    # Home & Garden
    ("plant pot labels", 9),
    ("succulent stickers", 9),
    ("home decor labels", 10),
    ("cushion care labels", 10),
    ("seed packet stickers", 11),
    ("garden tool labels", 11),
    # Fashion & Accessories
    ("jewellery box stickers", 12),
    ("handmade earring labels", 12),
    ("t-shirt care labels", 13),
    ("clothing brand stickers", 13),
    ("leather bag labels", 14),
    ("tote bag stickers", 14),
    # Pets
    ("dog treat labels", 15),
    ("organic pet food stickers", 15),
    ("cat toy labels", 16),
    ("pet grooming stickers", 16),
    # Tech & Gadgets
    ("laptop decal stickers", 17),
    ("phone case labels", 18),
    ("charger cable stickers", 18),
    # Stationery & Paper
    ("greeting card envelope seals", 19),
    ("thank you stickers", 19),
    ("planner stickers", 20),
    ("journal labels", 20),
    # Art & Craft
    ("paint tube labels", 21),
    ("craft kit stickers", 22),
    ("etsy seller packaging", 23),
    # Events & Weddings
    ("wedding favour labels", 24),
    ("save the date stickers", 24),
    ("event badge labels", 25),
    # Fitness & Sports
    ("protein powder labels", 26),
    ("gym supplement stickers", 26),
    ("sports water bottle labels", 27),
    # FBA / Generic business
    ("fragile handle with care stickers", 28),
    ("this way up labels", 28),
    ("thank you for your order stickers", 28),
    ("handmade with love labels", 28),
    ("small business stickers", 28),
    ("uk made stickers", 28),
    ("eco friendly packaging labels", 28),
    ("recyclable stickers", 28),
    ("biodegradable labels", 28),
    ("circular economy stickers", 28),
]

# Expand to ~1000 by duplicating with modifiers
MODIFIERS = ["", "custom ", "personalised ", "premium ", "luxury ", "vintage ", "minimal ", "kawaii ", "retro ", "holographic "]

async def main():
    dsn = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/b2b_stickers")
    conn = await asyncpg.connect(dsn)

    expanded = []
    for kw, industry_id in KEYWORDS:
        for mod in MODIFIERS:
            expanded.append((f"{mod}{kw}".strip(), industry_id))

    # Deduplicate
    seen = set()
    unique = []
    for kw, iid in expanded:
        if kw not in seen:
            seen.add(kw)
            unique.append((kw, iid))

    await conn.executemany(
        "INSERT INTO trends (keyword, industry_id, region) VALUES ($1, $2, 'UK') ON CONFLICT (keyword) DO NOTHING",
        unique[:1000]
    )

    count = await conn.fetchval("SELECT COUNT(*) FROM trends")
    print(f"Seeded {len(unique[:1000])} keywords. Total trends: {count}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
