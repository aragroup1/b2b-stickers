from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List

from app.core.auth import require_admin
from app.workers.tasks import generate_batch

router = APIRouter(prefix="/generation", tags=["generation"])


class BatchGenerationRequest(BaseModel):
    trend_ids: List[int]
    styles: List[str]
    designs_per_combo: int = 3
    mode: str = "production"


@router.post("/batch")
async def batch_generate(req: BatchGenerationRequest, background_tasks: BackgroundTasks, _=Depends(require_admin)):
    job = generate_batch.delay(
        trend_ids=req.trend_ids,
        styles=req.styles,
        designs_per_combo=req.designs_per_combo,
        mode=req.mode,
    )
    return {"job_id": str(job.id), "status": "queued"}


@router.get("/status")
async def generation_status(_=Depends(require_admin)):
    return {"message": "generation status"}
