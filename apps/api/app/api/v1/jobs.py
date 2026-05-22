from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from app.dependencies import get_db
from app.core.auth import require_admin

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
async def get_job(job_id: UUID, db=Depends(get_db), _=Depends(require_admin)):
    row = await db.fetchrow("SELECT * FROM jobs WHERE id = $1", job_id)
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(row)
