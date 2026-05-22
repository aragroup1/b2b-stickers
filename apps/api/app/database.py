import asyncpg
from loguru import logger

from app.config import settings

_db_pool: asyncpg.Pool | None = None


async def init_pool() -> asyncpg.Pool:
    global _db_pool
    _db_pool = await asyncpg.create_pool(
        settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
        min_size=5,
        max_size=20,
    )
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
