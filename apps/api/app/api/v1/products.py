from fastapi import APIRouter, Query, Depends
from typing import Optional

from app.dependencies import get_db
from app.core.auth import require_admin

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def list_products(
    status: Optional[str] = Query(None),
    min_quality: Optional[float] = Query(None),
    industry: Optional[str] = Query(None),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    _=Depends(require_admin),
):
    where_clauses = ["1=1"]
    params = []
    param_idx = 1

    if status:
        where_clauses.append(f"p.status = ${param_idx}")
        params.append(status)
        param_idx += 1
    if min_quality:
        where_clauses.append(f"a.quality_score >= ${param_idx}")
        params.append(min_quality)
        param_idx += 1
    if industry:
        where_clauses.append(f"i.slug = ${param_idx}")
        params.append(industry)
        param_idx += 1

    where_sql = " AND ".join(where_clauses)

    rows = await db.fetch(
        f"""
        SELECT p.id, p.slug, p.title, p.description, p.tags, p.status, p.metadata, p.created_at,
               a.image_url, a.quality_score, i.name as industry_name
        FROM products p
        JOIN artwork a ON p.artwork_id = a.id
        LEFT JOIN industries i ON p.industry_id = i.id
        WHERE {where_sql}
        ORDER BY p.created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """,
        *params, limit, offset
    )

    return {"products": [dict(r) for r in rows], "limit": limit, "offset": offset}


@router.get("/{id}")
async def get_product(id: int, db=Depends(get_db), _=Depends(require_admin)):
    row = await db.fetchrow(
        """
        SELECT p.*, a.image_url, a.quality_score, a.prompt, a.model_used, a.style
        FROM products p
        JOIN artwork a ON p.artwork_id = a.id
        WHERE p.id = $1
        """,
        id,
    )
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")

    product = dict(row)
    variants = await db.fetch(
        "SELECT * FROM sticker_variants WHERE product_id = $1", id
    )
    product["variants"] = [dict(v) for v in variants]
    return product
