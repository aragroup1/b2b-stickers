import asyncpg
from loguru import logger

from app.config import settings

_db_pool: asyncpg.Pool | None = None


async def init_pool() -> asyncpg.Pool:
    global _db_pool
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    # Log connection details (mask password)
    safe_url = url
    if "@" in safe_url:
        parts = safe_url.split("@")
        creds = parts[0].split(":")
        if len(creds) >= 2:
            safe_url = f"{creds[0]}:****@{parts[1]}"
    logger.info(f"Connecting to database: {safe_url}")
    _db_pool = await asyncpg.create_pool(
        url,
        min_size=5,
        max_size=20,
    )
    # Verify connection by querying current_database and checking for customers table
    async with _db_pool.acquire() as conn:
        db_name = await conn.fetchval("SELECT current_database()")
        schema = await conn.fetchval("SELECT current_schema()")
        logger.info(f"Connected to database: {db_name}, schema: {schema}")
        has_customers = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'customers')"
        )
        logger.info(f"Customers table exists: {has_customers}")
    logger.info("Database pool initialized")
    return _db_pool


async def close_pool():
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        logger.info("Database pool closed")


async def get_pool() -> asyncpg.Pool:
    if _db_pool is None:
        raise RuntimeError("Database pool not initialized")
    return _db_pool
