from fastapi import APIRouter, HTTPException, Depends, Query
from uuid import UUID
from typing import Optional, Literal

from app.dependencies import get_db
from app.core.auth import require_admin

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
async def list_jobs(
    status: Optional[Literal["running", "completed", "failed", "queued"]] = Query(None),
    kind: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    _=Depends(require_admin),
):
    where = ["1=1"]
    params = []
    param_idx = 1

    if status:
        where.append(f"status = ${param_idx}")
        params.append(status)
        param_idx += 1
    if kind:
        where.append(f"kind = ${param_idx}")
        params.append(kind)
        param_idx += 1

    where_sql = " AND ".join(where)

    rows = await db.fetch(
        f"""
        SELECT id, kind, status, params, progress, result, error,
               created_at, updated_at,
               EXTRACT(EPOCH FROM (COALESCE(updated_at, NOW()) - created_at)) as duration_seconds
        FROM jobs
        WHERE {where_sql}
        ORDER BY created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """,
        *params, limit, offset
    )

    # Get stats
    stats = await db.fetchrow("""
        SELECT
            COUNT(*) FILTER (WHERE status = 'running') as running,
            COUNT(*) FILTER (WHERE status = 'completed') as completed,
            COUNT(*) FILTER (WHERE status = 'failed') as failed,
            COUNT(*) FILTER (WHERE status = 'queued') as queued,
            COUNT(*) as total
        FROM jobs
    """)

    return {
        "jobs": [dict(r) for r in rows],
        "stats": dict(stats),
        "limit": limit,
        "offset": offset,
    }


@router.get("/stats")
async def get_job_stats(db=Depends(get_db), _=Depends(require_admin)):
    stats = await db.fetchrow("""
        SELECT
            COUNT(*) FILTER (WHERE status = 'running') as running,
            COUNT(*) FILTER (WHERE status = 'completed') as completed,
            COUNT(*) FILTER (WHERE status = 'failed') as failed,
            COUNT(*) FILTER (WHERE status = 'queued') as queued,
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') as last_24h,
            COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as last_7d
        FROM jobs
    """)

    # Get recent generation stats
    gen_stats = await db.fetchrow("""
        SELECT
            COUNT(*) as total_jobs,
            COALESCE(SUM((result->>'generated')::int), 0) as total_generated,
            AVG((progress->>'completed')::float / NULLIF((progress->>'total')::float, 0)) * 100 as avg_completion
        FROM jobs
        WHERE kind = 'generate_batch'
          AND created_at > NOW() - INTERVAL '7 days'
    """)

    return {
        "queue": dict(stats),
        "generation": {
            "total_jobs": gen_stats["total_jobs"] or 0,
            "total_generated": int(gen_stats["total_generated"] or 0),
            "avg_completion": round(gen_stats["avg_completion"] or 0, 1),
        }
    }


@router.get("/{job_id}")
async def get_job(job_id: UUID, db=Depends(get_db), _=Depends(require_admin)):
    row = await db.fetchrow("""
        SELECT id, kind, status, params, progress, result, error,
               created_at, updated_at,
               EXTRACT(EPOCH FROM (COALESCE(updated_at, NOW()) - created_at)) as duration_seconds
        FROM jobs WHERE id = $1
    """, job_id)
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(row)
