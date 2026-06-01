from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional

from app.core.auth import require_admin
from app.workers.tasks import generate_batch, generate_volume_weighted
from app.database import get_pool

router = APIRouter(prefix="/generation", tags=["generation"])


class BatchGenerationRequest(BaseModel):
    trend_ids: List[int]
    styles: List[str]
    designs_per_combo: int = 3
    mode: str = "production"


class VolumeWeightedRequest(BaseModel):
    target_total: int = 1000
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


@router.get("/plan")
async def generation_plan(target_total: int = 1000, _=Depends(require_admin)):
    """Preview the volume-weighted allocation without generating anything."""
    pool = await get_pool()
    
    trends = await pool.fetch(
        "SELECT id, keyword, search_volume, designs_generated FROM trends WHERE search_volume IS NOT NULL ORDER BY search_volume DESC"
    )
    
    if not trends:
        return {"error": "No trends with search volume found"}
    
    total_volume = sum(t["search_volume"] or 0 for t in trends)
    current_products = await pool.fetchval("SELECT COUNT(*) FROM products")
    
    allocations = []
    for trend in trends:
        vol = trend["search_volume"] or 0
        target_designs = max(2, round((vol / total_volume) * target_total))
        already = trend["designs_generated"] or 0
        remaining = max(0, target_designs - already)
        
        allocations.append({
            "id": trend["id"],
            "keyword": trend["keyword"],
            "search_volume": vol,
            "volume_percent": round((vol / total_volume) * 100, 1),
            "target_designs": target_designs,
            "already_generated": already,
            "remaining": remaining,
            "demand_tier": "high" if vol >= 10000 else "medium" if vol >= 3000 else "low",
        })
    
    # Adjust to hit target
    current_sum = sum(a["target_designs"] for a in allocations)
    diff = target_total - current_sum
    if diff != 0:
        allocations[0]["target_designs"] += diff
        allocations[0]["remaining"] = max(0, allocations[0]["target_designs"] - allocations[0]["already_generated"])
    
    total_to_generate = sum(a["remaining"] for a in allocations)
    
    # Cost estimate (mock mode = £0, real mode = ~£0.03/image)
    cost_per_image = 0.03  # flux-schnell average
    estimated_cost = total_to_generate * cost_per_image
    
    return {
        "target_total": target_total,
        "current_products": current_products,
        "total_trends": len(trends),
        "total_search_volume": total_volume,
        "total_to_generate": total_to_generate,
        "estimated_cost_gbp": round(estimated_cost, 2),
        "estimated_time_minutes": round(total_to_generate * 0.5),  # ~30s per product
        "allocations": allocations,
    }


@router.post("/volume-weighted")
async def volume_weighted_generate(req: VolumeWeightedRequest, _=Depends(require_admin)):
    """Queue a volume-weighted generation job targeting ~1000 products."""
    job = generate_volume_weighted.delay(
        target_total=req.target_total,
        mode=req.mode,
    )
    return {
        "job_id": str(job.id),
        "status": "queued",
        "target_total": req.target_total,
        "message": f"Volume-weighted generation queued. Target: {req.target_total} products.",
    }


@router.get("/status")
async def generation_status(_=Depends(require_admin)):
    return {"message": "generation status"}
