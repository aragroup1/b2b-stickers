from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Literal

from app.dependencies import get_db
from app.core.auth import require_admin
from app.utils.helpers import generate_unique_slug

router = APIRouter(prefix="/approval", tags=["approval"])


class BulkApprovalRequest(BaseModel):
    product_ids: List[int]
    action: Literal["approve", "reject"]


@router.post("/bulk")
async def bulk_approve(req: BulkApprovalRequest, db=Depends(get_db), _=Depends(require_admin)):
    new_status = "approved" if req.action == "approve" else "archived"

    approved_ids = []
    async with db.transaction():
        for pid in req.product_ids:
            if req.action == "approve":
                row = await db.fetchrow(
                    "SELECT title FROM products WHERE id = $1", pid
                )
                if row:
                    slug = await generate_unique_slug(row["title"])
                    await db.execute(
                        "UPDATE products SET status = $1, slug = $2 WHERE id = $3",
                        new_status, slug, pid
                    )
                    approved_ids.append(pid)
            else:
                await db.execute(
                    "UPDATE products SET status = $1 WHERE id = $2",
                    new_status, pid
                )

    # Generate lifestyle mockups for approved products (after the transaction commits)
    if approved_ids:
        from app.workers.tasks import composite_product_mockups
        for pid in approved_ids:
            composite_product_mockups.delay(pid)

    return {"updated": len(req.product_ids), "status": new_status}


class AutoApprovalRequest(BaseModel):
    min_quality_score: float = 70.0
    limit: int = 100


@router.post("/auto")
async def auto_approve(req: AutoApprovalRequest, db=Depends(get_db)):
    rows = await db.fetch(
        """
        SELECT p.id, p.title
        FROM products p
        JOIN artwork a ON p.artwork_id = a.id
        WHERE p.status = 'pending_approval'
          AND a.quality_score >= $1
        LIMIT $2
        """,
        req.min_quality_score,
        req.limit,
    )

    approved = 0
    approved_ids = []
    async with db.transaction():
        for row in rows:
            slug = await generate_unique_slug(row["title"])
            await db.execute(
                "UPDATE products SET status = 'approved', slug = $1 WHERE id = $2",
                slug, row["id"],
            )
            approved += 1
            approved_ids.append(row["id"])

    from app.workers.tasks import composite_product_mockups
    for pid in approved_ids:
        composite_product_mockups.delay(pid)

    return {"approved": approved}
