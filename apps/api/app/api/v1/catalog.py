from fastapi import APIRouter, Query, Depends
from typing import Optional

from app.dependencies import get_db
from app.config import settings
from app.utils.cache import cache_get, cache_set

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/products")
async def list_products(
    industry: Optional[str] = Query(None),
    min_pack: Optional[int] = Query(None),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
):
    # Try cache first
    cache_key = f"catalog:products:{industry}:{min_pack}:{limit}:{offset}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    where_clauses = ["p.status = 'approved'"]
    params: list = []
    param_idx = 1

    if industry:
        where_clauses.append(f"i.slug = ${param_idx}")
        params.append(industry)
        param_idx += 1
    if min_pack:
        where_clauses.append(f"EXISTS (SELECT 1 FROM sticker_variants sv WHERE sv.product_id = p.id AND sv.pack_quantity >= ${param_idx})")
        params.append(min_pack)
        param_idx += 1

    where_sql = " AND ".join(where_clauses)

    rows = await db.fetch(
        f"""
        SELECT p.id, p.slug, p.title, p.description, p.tags, p.status, p.metadata,
               a.image_url, i.name as industry_name
        FROM products p
        JOIN artwork a ON p.artwork_id = a.id
        LEFT JOIN industries i ON p.industry_id = i.id
        WHERE {where_sql}
        ORDER BY p.created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """,
        *params, limit, offset
    )

    products = [dict(r) for r in rows]

    # Attach variants with VAT-inclusive pricing
    for prod in products:
        variants = await db.fetch(
            "SELECT * FROM sticker_variants WHERE product_id = $1 ORDER BY size_inches, pack_quantity",
            prod["id"]
        )
        prod["variants"] = []
        for v in variants:
            vd = dict(v)
            from app.core.stickers.config import get_recurring_price, compute_vat_inclusive_price
            vd["recurring_price"] = get_recurring_price(v["retail_price"])
            vd["retail_price_vat"] = compute_vat_inclusive_price(v["retail_price"])
            vd["recurring_price_vat"] = compute_vat_inclusive_price(vd["recurring_price"])
            prod["variants"].append(vd)

    result = {"products": products, "limit": limit, "offset": offset}
    await cache_set(cache_key, result, ttl=60)
    return result


@router.get("/products/{slug}")
async def product_detail(slug: str, db=Depends(get_db)):
    # Try cache first
    cache_key = f"catalog:product:{slug}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    row = await db.fetchrow(
        """
        SELECT p.id, p.slug, p.title, p.description, p.tags, p.status, p.metadata,
               a.image_url, a.prompt, a.model_used, a.style, a.quality_score,
               i.name as industry_name
        FROM products p
        JOIN artwork a ON p.artwork_id = a.id
        LEFT JOIN industries i ON p.industry_id = i.id
        WHERE p.slug = $1 AND p.status = 'approved'
        """,
        slug,
    )

    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")

    product = dict(row)

    variants = await db.fetch(
        "SELECT * FROM sticker_variants WHERE product_id = $1 ORDER BY size_inches, pack_quantity",
        product["id"]
    )
    product["variants"] = []
    for v in variants:
        vd = dict(v)
        from app.core.stickers.config import get_recurring_price, compute_vat_inclusive_price
        vd["recurring_price"] = get_recurring_price(v["retail_price"])
        vd["retail_price_vat"] = compute_vat_inclusive_price(v["retail_price"])
        vd["recurring_price_vat"] = compute_vat_inclusive_price(vd["recurring_price"])
        product["variants"].append(vd)

    await cache_set(cache_key, product, ttl=300)
    return product
