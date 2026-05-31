from fastapi import APIRouter
import redis.asyncio as aioredis
from api.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/")
async def health_check():
    # Check Redis
    try:
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        redis_ok = True
        await r.aclose()
    except Exception:
        redis_ok = False

    return {
        "status": "ok",
        "redis": "ok" if redis_ok else "error",
        "env": settings.app_env,
    }
