from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from typing import Optional, List

from app.dependencies import get_db
from app.core.auth import require_admin

router = APIRouter(prefix="/listings", tags=["listings"])


class PushListingsRequest(BaseModel):
    product_ids: List[int]
    platforms: List[str]  # "amazon_uk", "ebay_uk"


@router.post("/push")
async def push_listings(req: PushListingsRequest, db=Depends(get_db), _=Depends(require_admin)):
    results = []
    for pid in req.product_ids:
        for platform in req.platforms:
            # Upsert listing row
            await db.execute(
                """
                INSERT INTO platform_listings (product_id, platform, status)
                VALUES ($1, $2, 'queued')
                ON CONFLICT (product_id, platform) DO UPDATE SET status = 'queued'
                """,
                pid, platform
            )
            results.append({"product_id": pid, "platform": platform, "status": "queued"})

    return {"queued": len(results), "results": results}


@router.get("")
async def list_listings(
    channel: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    _=Depends(require_admin),
):
    where_clauses = ["1=1"]
    params = []
    param_idx = 1

    if channel:
        where_clauses.append(f"platform = ${param_idx}")
        params.append(channel)
        param_idx += 1
    if status:
        where_clauses.append(f"pl.status = ${param_idx}")
        params.append(status)
        param_idx += 1

    where_sql = " AND ".join(where_clauses)

    rows = await db.fetch(
        f"""
        SELECT pl.*, p.title as product_title, p.slug
        FROM platform_listings pl
        JOIN products p ON pl.product_id = p.id
        WHERE {where_sql}
        ORDER BY pl.created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """,
        *params, limit, offset
    )

    return {"listings": [dict(r) for r in rows], "limit": limit, "offset": offset}
