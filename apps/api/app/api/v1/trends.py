from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from typing import Optional

from app.dependencies import get_db
from app.core.auth import require_admin

router = APIRouter(prefix="/trends", tags=["trends"])


class CreateTrendRequest(BaseModel):
    keyword: str
    industry_id: Optional[int] = None
    search_volume: Optional[int] = None
    trend_score: Optional[float] = None
    category: Optional[str] = None


@router.get("")
async def list_trends(
    industry: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    _=Depends(require_admin),
):
    where = "1=1"
    params = []
    if industry:
        where = "i.slug = $1"
        params.append(industry)

    rows = await db.fetch(
        f"""
        SELECT t.*, i.name as industry_name
        FROM trends t
        LEFT JOIN industries i ON t.industry_id = i.id
        WHERE {where}
        ORDER BY t.created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
        """,
        *params, limit, offset
    )
    return {"trends": [dict(r) for r in rows], "limit": limit, "offset": offset}


@router.post("")
async def create_trend(req: CreateTrendRequest, db=Depends(get_db), _=Depends(require_admin)):
    id = await db.fetchval(
        """
        INSERT INTO trends (keyword, industry_id, search_volume, trend_score, category, region)
        VALUES ($1, $2, $3, $4, $5, 'UK')
        RETURNING id
        """,
        req.keyword, req.industry_id, req.search_volume, req.trend_score, req.category
    )
    return {"id": id, "keyword": req.keyword}


@router.get("/analytics")
async def trends_analytics(db=Depends(get_db)):
    total = await db.fetchval("SELECT COUNT(*) FROM trends")
    with_designs = await db.fetchval("SELECT COUNT(*) FROM trends WHERE designs_generated > 0")
    return {"total": total, "with_designs": with_designs}
