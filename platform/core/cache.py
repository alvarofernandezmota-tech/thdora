import json
import redis.asyncio as aioredis
from .config import settings

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def cache_agent_config(agent_id: str, config: dict) -> None:
    """Cachea la config de un agente para evitar hits a BD en cada mensaje."""
    r = await get_redis()
    await r.setex(
        f"agent:config:{agent_id}",
        settings.redis_agent_cache_ttl,
        json.dumps(config)
    )


async def get_cached_agent_config(agent_id: str) -> dict | None:
    r = await get_redis()
    data = await r.get(f"agent:config:{agent_id}")
    return json.loads(data) if data else None


async def invalidate_agent_cache(agent_id: str) -> None:
    r = await get_redis()
    await r.delete(f"agent:config:{agent_id}")
