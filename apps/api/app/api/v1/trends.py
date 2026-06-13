import csv
import io

from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from typing import Optional, Literal

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
    category: Optional[str] = Query(None),
    sort_by: Literal["search_volume", "trend_score", "created_at", "designs_generated"] = Query("search_volume"),
    sort_order: Literal["asc", "desc"] = Query("desc"),
    has_search_volume: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    _=Depends(require_admin),
):
    where_clauses = ["1=1"]
    params = []
    param_idx = 1

    if industry:
        where_clauses.append(f"i.slug = ${param_idx}")
        params.append(industry)
        param_idx += 1
    if category:
        where_clauses.append(f"t.category = ${param_idx}")
        params.append(category)
        param_idx += 1
    if has_search_volume is True:
        where_clauses.append("t.search_volume IS NOT NULL")
    elif has_search_volume is False:
        where_clauses.append("t.search_volume IS NULL")

    where_sql = " AND ".join(where_clauses)

    # Validate sort column
    allowed_sort = {"search_volume": "t.search_volume", "trend_score": "t.trend_score",
                    "created_at": "t.created_at", "designs_generated": "t.designs_generated"}
    sort_col = allowed_sort.get(sort_by, "t.search_volume")
    order_sql = "DESC" if sort_order == "desc" else "ASC"

    rows = await db.fetch(
        f"""
        SELECT t.*, i.name as industry_name,
               COUNT(DISTINCT p.id) as product_count
        FROM trends t
        LEFT JOIN industries i ON t.industry_id = i.id
        LEFT JOIN products p ON p.artwork_id IN (
            SELECT a.id FROM artwork a WHERE a.trend_id = t.id
        )
        WHERE {where_sql}
        GROUP BY t.id, i.name
        ORDER BY {sort_col} {order_sql} NULLS LAST
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """,
        *params, limit, offset
    )

    # Get categories for filtering
    categories = await db.fetch("SELECT DISTINCT category FROM trends WHERE category IS NOT NULL ORDER BY category")

    return {
        "trends": [dict(r) for r in rows],
        "categories": [c["category"] for c in categories],
        "limit": limit,
        "offset": offset
    }


@router.get("/categories")
async def list_categories(db=Depends(get_db), _=Depends(require_admin)):
    rows = await db.fetch("""
        SELECT category, COUNT(*) as trend_count,
               SUM(search_volume) as total_search_volume,
               AVG(trend_score) as avg_trend_score
        FROM trends
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY total_search_volume DESC NULLS LAST
    """)
    return {"categories": [dict(r) for r in rows]}


@router.get("/seo-demand")
async def get_seo_demand_report(
    min_volume: Optional[int] = Query(100),
    db=Depends(get_db),
    _=Depends(require_admin),
):
    """Get trends ranked by SEO demand (search volume) with generation gaps."""
    rows = await db.fetch("""
        SELECT t.*, i.name as industry_name,
               COALESCE(t.designs_generated, 0) as generated,
               COALESCE(t.designs_allocated, 0) as allocated,
               CASE
                   WHEN t.search_volume >= 10000 THEN 'high'
                   WHEN t.search_volume >= 1000 THEN 'medium'
                   ELSE 'low'
               END as demand_tier
        FROM trends t
        LEFT JOIN industries i ON t.industry_id = i.id
        WHERE t.search_volume IS NOT NULL
          AND t.search_volume >= $1
        ORDER BY t.search_volume DESC
    """, min_volume)

    return {
        "trends": [dict(r) for r in rows],
        "summary": {
            "total_with_volume": len(rows),
            "high_demand": sum(1 for r in rows if r["demand_tier"] == "high"),
            "medium_demand": sum(1 for r in rows if r["demand_tier"] == "medium"),
            "low_demand": sum(1 for r in rows if r["demand_tier"] == "low"),
            "underserved": sum(1 for r in rows if r["generated"] < r["allocated"]),
        }
    }


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
    with_volume = await db.fetchval("SELECT COUNT(*) FROM trends WHERE search_volume IS NOT NULL")
    total_volume = await db.fetchval("SELECT COALESCE(SUM(search_volume), 0) FROM trends")
    return {
        "total": total,
        "with_designs": with_designs,
        "with_search_volume": with_volume,
        "total_search_volume": int(total_volume),
    }


# ---------------------------------------------------------------------------
# Real search-volume signal: Keyword Planner import (#1) + Google Trends (#2)
# ---------------------------------------------------------------------------

def _num(s: str) -> Optional[int]:
    """Parse a single number, tolerating commas and K/M suffixes."""
    s = s.strip().upper().replace(",", "")
    mult = 1
    if s.endswith("K"):
        mult, s = 1_000, s[:-1]
    elif s.endswith("M"):
        mult, s = 1_000_000, s[:-1]
    try:
        return int(float(s) * mult)
    except ValueError:
        return None


def _parse_volume(raw: str) -> Optional[int]:
    """Parse a Keyword Planner volume cell: plain, K/M suffix, or a range -> midpoint."""
    s = (raw or "").strip().replace('"', "").replace(" ", "").replace("\xa0", " ")
    if not s:
        return None
    for sep in ("–", "—", " to ", " - ", "-"):
        if sep in s:
            parts = [p for p in (x.strip() for x in s.split(sep)) if p]
            if len(parts) == 2:
                lo, hi = _num(parts[0]), _num(parts[1])
                if lo is not None and hi is not None:
                    return int((lo + hi) / 2)
            break
    return _num(s)


def _parse_keyword_planner(text: str) -> list[tuple[str, int]]:
    """Parse a pasted Keyword Planner export (CSV or TSV) into (keyword, volume) pairs.

    Detects the header row (cells containing 'keyword' and 'search'); falls back to
    first column = keyword and first parseable numeric column = volume.
    """
    text = (text or "").replace("﻿", "")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    delim = "\t" if "\t" in lines[0] else ","
    rows = list(csv.reader(io.StringIO("\n".join(lines)), delimiter=delim))

    kw_col, vol_col, start = 0, None, 0
    for idx, row in enumerate(rows[:5]):
        lowered = [c.strip().lower() for c in row]
        kw_hit = next((i for i, c in enumerate(lowered) if "keyword" in c), None)
        vol_hit = next((i for i, c in enumerate(lowered) if "search" in c), None)
        if kw_hit is not None and vol_hit is not None:
            kw_col, vol_col, start = kw_hit, vol_hit, idx + 1
            break

    out: list[tuple[str, int]] = []
    for row in rows[start:]:
        if not row or len(row) <= kw_col:
            continue
        keyword = row[kw_col].strip()
        if not keyword:
            continue
        vol = _parse_volume(row[vol_col]) if (vol_col is not None and len(row) > vol_col) else None
        if vol is None:
            for i, cell in enumerate(row):
                if i == kw_col:
                    continue
                vol = _parse_volume(cell)
                if vol is not None:
                    break
        if vol is not None:
            out.append((keyword, vol))
    return out


class ImportVolumesRequest(BaseModel):
    csv_text: str


@router.post("/import-volumes")
async def import_volumes(req: ImportVolumesRequest, db=Depends(get_db), _=Depends(require_admin)):
    """Import real search volumes from a pasted Google Keyword Planner export.

    Matches existing trends by keyword (case-insensitive) and sets search_volume +
    volume_source='keyword_planner'. Unmatched keywords are reported, not created.
    """
    pairs = _parse_keyword_planner(req.csv_text)
    if not pairs:
        return {
            "parsed": 0, "matched": 0, "unmatched": [],
            "error": "No keyword/volume rows found. Paste the Keyword Planner CSV/TSV export.",
        }
    matched, unmatched = 0, []
    for keyword, volume in pairs:
        updated_id = await db.fetchval(
            "UPDATE trends SET search_volume = $1, volume_source = 'keyword_planner' "
            "WHERE LOWER(keyword) = LOWER($2) RETURNING id",
            volume, keyword,
        )
        if updated_id:
            matched += 1
        else:
            unmatched.append(keyword)
    return {"parsed": len(pairs), "matched": matched, "unmatched": unmatched}


@router.post("/refresh-volumes")
async def refresh_volumes(limit: int = Query(200, ge=1, le=1000), _=Depends(require_admin)):
    """Queue a Google Trends refresh for trends lacking Keyword Planner data."""
    from app.workers.tasks import refresh_trend_volumes

    job = refresh_trend_volumes.delay(limit=limit)
    return {"job_id": str(job.id), "status": "queued"}
