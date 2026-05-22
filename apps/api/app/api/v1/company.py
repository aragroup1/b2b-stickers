from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import httpx

from app.dependencies import get_db
from app.config import settings

router = APIRouter(prefix="/company", tags=["company"])


class CompanyVerifyRequest(BaseModel):
    company_number: str  # UK Companies House number
    customer_id: int


@router.post("/verify")
async def verify_company(req: CompanyVerifyRequest, db=Depends(get_db)):
    """Verify a UK company via Companies House API."""
    # Check if customer exists
    customer = await db.fetchrow("SELECT * FROM customers WHERE id = $1", req.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Call Companies House API
    api_key = settings.COMPANIES_HOUSE_API_KEY
    if not api_key:
        # Return mock verification in development
        if settings.ENV == "development":
            await db.execute(
                "UPDATE customers SET company_number = $1, company_name = $2 WHERE id = $3",
                req.company_number, f"Demo Company {req.company_number}", req.customer_id,
            )
            return {
                "verified": True,
                "company_number": req.company_number,
                "company_name": f"Demo Company {req.company_number}",
                "status": "active",
                "note": "Development mode — no API key",
            }
        raise HTTPException(status_code=500, detail="Companies House API key not configured")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.company-information.service.gov.uk/company/{req.company_number}",
                auth=(api_key, ""),
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()

        company_name = data.get("company_name")
        company_status = data.get("company_status")

        await db.execute(
            "UPDATE customers SET company_number = $1, company_name = $2 WHERE id = $3",
            req.company_number, company_name, req.customer_id,
        )

        return {
            "verified": company_status == "active",
            "company_number": req.company_number,
            "company_name": company_name,
            "status": company_status,
            "date_of_creation": data.get("date_of_creation"),
            "registered_office_address": data.get("registered_office_address"),
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Company not found")
        raise HTTPException(status_code=500, detail=f"Companies House API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_companies(query: str):
    """Search Companies House for a company by name."""
    api_key = settings.COMPANIES_HOUSE_API_KEY
    if not api_key:
        return {"results": [], "note": "Companies House API key not configured"}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.company-information.service.gov.uk/search/companies",
                params={"q": query},
                auth=(api_key, ""),
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()

        results = [
            {
                "company_number": item.get("company_number"),
                "company_name": item.get("title"),
                "company_status": item.get("company_status"),
                "address": item.get("address_snippet"),
            }
            for item in data.get("items", [])[:10]
        ]

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
