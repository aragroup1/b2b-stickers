from fastapi import Request, HTTPException, status, Depends
from app.database import get_pool
import jwt
from app.config import settings


async def get_db(request: Request):
    """FastAPI dependency that yields the asyncpg pool."""
    return await get_pool()


async def get_current_customer(request: Request, db=Depends(get_db)):
    """Authenticate customer via session cookie and return customer record."""
    auth = request.cookies.get("session")
    if not auth:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(auth, settings.JWT_SECRET, algorithms=["HS256"])
        row = await db.fetchrow("SELECT * FROM customers WHERE id = $1", payload["customer_id"])
        if not row:
            raise HTTPException(status_code=401, detail="Customer not found")
        return dict(row)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session")
