from fastapi import APIRouter, Query, Depends
from typing import Optional

from app.dependencies import get_db
from app.utils.cache import cache_get, cache_set

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/products")
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
):
    """Full-text search across products using Postgres tsvector."""
    cache_key = f"search:products:{q}:{limit}:{offset}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    # Use Postgres full-text search
    rows = await db.fetch(
        """
        SELECT p.id, p.slug, p.title, p.description, p.tags, a.image_url,
               ts_rank(
                   setweight(to_tsvector('english', COALESCE(p.title, '')), 'A') ||
                   setweight(to_tsvector('english', COALESCE(p.description, '')), 'B') ||
                   setweight(to_tsvector('english', COALESCE(array_to_string(p.tags, ' '), '')), 'C'),
                   plainto_tsquery('english', $1)
               ) as rank
        FROM products p
        JOIN artwork a ON p.artwork_id = a.id
        WHERE p.status = 'approved'
          AND (
              to_tsvector('english', COALESCE(p.title, '')) ||
              to_tsvector('english', COALESCE(p.description, '')) ||
              to_tsvector('english', COALESCE(array_to_string(p.tags, ' '), ''))
          ) @@ plainto_tsquery('english', $1)
        ORDER BY rank DESC, p.created_at DESC
        LIMIT $2 OFFSET $3
        """,
        q, limit, offset,
    )

    products = [dict(r) for r in rows]

    # Attach variants
    for prod in products:
        variants = await db.fetch(
            "SELECT * FROM sticker_variants WHERE product_id = $1 ORDER BY size_inches, pack_quantity",
            prod["id"]
        )
        from app.core.stickers.config import get_recurring_price
        prod["variants"] = []
        for v in variants:
            vd = dict(v)
            vd["recurring_price"] = get_recurring_price(v["retail_price"])
            prod["variants"].append(vd)

    result = {"products": products, "query": q, "limit": limit, "offset": offset}
    await cache_set(cache_key, result, ttl=120)
    return result


@router.get("/suggest")
async def search_suggestions(
    q: str = Query(..., min_length=2),
    limit: int = Query(8, ge=1, le=20),
    db=Depends(get_db),
):
    """Get search suggestions based on product titles and tags."""
    cache_key = f"search:suggest:{q}:{limit}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    rows = await db.fetch(
        """
        SELECT DISTINCT p.title, p.slug
        FROM products p
        WHERE p.status = 'approved'
          AND (
              p.title ILIKE $1
              OR EXISTS (
                  SELECT 1 FROM unnest(p.tags) tag
                  WHERE tag ILIKE $1
              )
          )
        LIMIT $2
        """,
        f"%{q}%", limit,
    )

    result = {
        "suggestions": [
            {"title": r["title"], "slug": r["slug"]}
            for r in rows
        ]
    }
    await cache_set(cache_key, result, ttl=300)
    return result
