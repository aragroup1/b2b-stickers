"""Simple caching utilities using Redis."""

import json
from typing import Optional, Any
import redis.asyncio as redis
from app.config import settings

_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Get a cached value by key."""
    try:
        r = await get_redis()
        data = await r.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """Set a cached value with TTL in seconds."""
    try:
        r = await get_redis()
        await r.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception:
        return False


async def cache_delete(key: str) -> bool:
    """Delete a cached value by key."""
    try:
        r = await get_redis()
        await r.delete(key)
        return True
    except Exception:
        return False
