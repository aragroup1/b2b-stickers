from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import get_db
from app.core.auth import require_admin

router = APIRouter(prefix="/industries", tags=["industries"])


class CreateIndustryRequest(BaseModel):
    slug: str
    name: str
    parent_id: int | None = None


@router.get("")
async def list_industries(db=Depends(get_db), _=Depends(require_admin)):
    rows = await db.fetch("SELECT * FROM industries ORDER BY name")
    return {"industries": [dict(r) for r in rows]}


@router.post("")
async def create_industry(req: CreateIndustryRequest, db=Depends(get_db), _=Depends(require_admin)):
    id = await db.fetchval(
        "INSERT INTO industries (slug, name, parent_id) VALUES ($1, $2, $3) RETURNING id",
        req.slug, req.name, req.parent_id
    )
    return {"id": id, "slug": req.slug, "name": req.name}
