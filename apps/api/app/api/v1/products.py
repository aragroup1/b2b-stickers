from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, Literal, List

from app.dependencies import get_db
from app.core.auth import require_admin
from app.utils.helpers import generate_unique_slug

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def list_products(
    status: Optional[str] = Query(None),
    min_quality: Optional[float] = Query(None),
    industry: Optional[str] = Query(None),
    style: Optional[str] = Query(None),
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
    if style:
        where_clauses.append(f"a.style = ${param_idx}")
        params.append(style)
        param_idx += 1

    where_sql = " AND ".join(where_clauses)

    rows = await db.fetch(
        f"""
        SELECT p.id, p.slug, p.title, p.description, p.tags, p.status, p.metadata, p.created_at,
               a.image_url, a.quality_score, a.style, a.prompt, i.name as industry_name,
               t.keyword as trend_keyword, t.search_volume
        FROM products p
        JOIN artwork a ON p.artwork_id = a.id
        LEFT JOIN industries i ON p.industry_id = i.id
        LEFT JOIN trends t ON a.trend_id = t.id
        WHERE {where_sql}
        ORDER BY p.created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """,
        *params, limit, offset
    )

    # Get status counts for gallery tabs
    counts = await db.fetch("""
        SELECT status, COUNT(*) as count
        FROM products
        GROUP BY status
        ORDER BY count DESC
    """)

    # Get available styles for filter
    styles = await db.fetch("""
        SELECT DISTINCT a.style, COUNT(*) as count
        FROM artwork a
        JOIN products p ON p.artwork_id = a.id
        WHERE a.style IS NOT NULL
        GROUP BY a.style
        ORDER BY count DESC
    """)

    return {
        "products": [dict(r) for r in rows],
        "status_counts": {r["status"]: r["count"] for r in counts},
        "styles": [{"name": r["style"], "count": r["count"]} for r in styles],
        "limit": limit,
        "offset": offset,
    }


@router.get("/gallery")
async def get_gallery(
    status: Optional[Literal["pending_approval", "approved", "active", "archived", "all"]] = Query("all"),
    style: Optional[str] = Query(None),
    sort_by: Literal["newest", "quality", "search_volume"] = Query("newest"),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    _=Depends(require_admin),
):
    where_clauses = ["1=1"]
    params = []
    param_idx = 1

    if status and status != "all":
        where_clauses.append(f"p.status = ${param_idx}")
        params.append(status)
        param_idx += 1
    if style:
        where_clauses.append(f"a.style = ${param_idx}")
        params.append(style)
        param_idx += 1

    where_sql = " AND ".join(where_clauses)

    sort_map = {
        "newest": "p.created_at DESC",
        "quality": "a.quality_score DESC NULLS LAST",
        "search_volume": "t.search_volume DESC NULLS LAST",
    }
    order_sql = sort_map.get(sort_by, "p.created_at DESC")

    rows = await db.fetch(
        f"""
        SELECT p.id, p.slug, p.title, p.status, p.created_at,
               a.image_url, a.quality_score, a.style, a.prompt,
               t.keyword as trend_keyword, t.search_volume,
               i.name as industry_name
        FROM products p
        JOIN artwork a ON p.artwork_id = a.id
        LEFT JOIN trends t ON a.trend_id = t.id
        LEFT JOIN industries i ON p.industry_id = i.id
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """,
        *params, limit, offset
    )

    return {
        "products": [dict(r) for r in rows],
        "limit": limit,
        "offset": offset,
    }


@router.get("/{id}")
async def get_product(id: int, db=Depends(get_db), _=Depends(require_admin)):
    row = await db.fetchrow(
        """
        SELECT p.*, a.image_url, a.quality_score, a.prompt, a.model_used, a.style,
               a.negative_prompt, a.generation_cost,
               t.keyword as trend_keyword, t.search_volume, t.trend_score,
               i.name as industry_name
        FROM products p
        JOIN artwork a ON p.artwork_id = a.id
        LEFT JOIN trends t ON a.trend_id = t.id
        LEFT JOIN industries i ON p.industry_id = i.id
        WHERE p.id = $1
        """,
        id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    variants = await db.fetch(
        "SELECT * FROM sticker_variants WHERE product_id = $1", id
    )

    result = dict(row)
    result["variants"] = [dict(v) for v in variants]
    return result


@router.patch("/{id}/status")
async def update_product_status(
    id: int,
    status: Literal["pending_approval", "approved", "active", "paused", "archived"],
    db=Depends(get_db),
    _=Depends(require_admin),
):
    if status == "approved":
        row = await db.fetchrow("SELECT title FROM products WHERE id = $1", id)
        if row:
            slug = await generate_unique_slug(row["title"])
            await db.execute(
                "UPDATE products SET status = $1, slug = $2 WHERE id = $3",
                status, slug, id
            )
    else:
        await db.execute(
            "UPDATE products SET status = $1 WHERE id = $2",
            status, id
        )
    return {"id": id, "status": status}


@router.post("/bulk-status")
async def bulk_update_status(
    product_ids: List[int],
    status: Literal["pending_approval", "approved", "active", "paused", "archived"],
    db=Depends(get_db),
    _=Depends(require_admin),
):
    updated = 0
    async with db.transaction():
        for pid in product_ids:
            if status == "approved":
                row = await db.fetchrow("SELECT title FROM products WHERE id = $1", pid)
                if row:
                    slug = await generate_unique_slug(row["title"])
                    await db.execute(
                        "UPDATE products SET status = $1, slug = $2 WHERE id = $3",
                        status, slug, pid
                    )
                    updated += 1
            else:
                await db.execute(
                    "UPDATE products SET status = $1 WHERE id = $2",
                    status, pid
                )
                updated += 1

    return {"updated": updated, "status": status}
