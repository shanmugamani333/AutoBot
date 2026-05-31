"""
Redis client — three responsibilities:
1. Session management  (conversation history per user)
2. Points balance cache (fast reads, invalidated on write)
3. Rate limiting       (per-user message counter)
"""

import json
import redis
from typing import Optional
from api.config import settings
import structlog

log = structlog.get_logger()

# ── Connection pool ───────────────────────────────────────────────────────────
_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=20,
    decode_responses=True,
)

def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=_pool)


# ── Session management ────────────────────────────────────────────────────────

def get_session(telegram_id: int) -> list[dict]:
    """
    Load the last N conversation turns for a user.
    Returns empty list if no session exists (new user or expired).
    """
    r = get_redis()
    key = f"session:{telegram_id}"
    raw = r.get(key)
    if not raw:
        return []
    return json.loads(raw)


def save_session(telegram_id: int, turns: list[dict]) -> None:
    """
    Save conversation turns to Redis.
    Keeps only the last MAX_SESSION_TURNS turns.
    Resets TTL on every save.
    """
    r = get_redis()
    key = f"session:{telegram_id}"
    trimmed = turns[-settings.MAX_SESSION_TURNS:]
    r.set(key, json.dumps(trimmed), ex=settings.SESSION_TTL_SECONDS)


def clear_session(telegram_id: int) -> None:
    """Delete the session (e.g. after 30 min inactivity or explicit /start)."""
    get_redis().delete(f"session:{telegram_id}")


def append_to_session(telegram_id: int, role: str, content: str) -> list[dict]:
    """
    Add one turn to the session and return the updated list.
    role is either 'user' or 'assistant'.
    """
    turns = get_session(telegram_id)
    turns.append({"role": role, "content": content})
    save_session(telegram_id, turns)
    return turns[-settings.MAX_SESSION_TURNS:]


# ── Points cache ──────────────────────────────────────────────────────────────

POINTS_CACHE_TTL = 600  # 10 minutes

def get_cached_points(telegram_id: int) -> Optional[float]:
    """Return cached points balance or None if cache miss."""
    r = get_redis()
    val = r.get(f"points:{telegram_id}")
    return float(val) if val is not None else None


def set_cached_points(telegram_id: int, balance: float) -> None:
    """Cache the points balance for 10 minutes."""
    get_redis().set(f"points:{telegram_id}", str(balance), ex=POINTS_CACHE_TTL)


def invalidate_points_cache(telegram_id: int) -> None:
    """Call this whenever a loyalty transaction is written."""
    get_redis().delete(f"points:{telegram_id}")


# ── Rate limiting ─────────────────────────────────────────────────────────────

def check_rate_limit(telegram_id: int) -> bool:
    """
    Returns True if the user is within their rate limit.
    Returns False if they have exceeded MAX messages per minute.
    Uses a sliding 60-second window counter.
    """
    r = get_redis()
    key = f"rate:{telegram_id}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)  # first message in window — set 60s TTL
    if count > settings.RATE_LIMIT_MESSAGES_PER_MINUTE:
        log.warning("rate_limit_exceeded", telegram_id=telegram_id, count=count)
        return False
    return True


# ── Dispute count (abuse prevention) ─────────────────────────────────────────

def get_open_dispute_count(telegram_id: int) -> int:
    """Read the open dispute counter for this user."""
    val = get_redis().get(f"disputes_open:{telegram_id}")
    return int(val) if val else 0


def increment_open_disputes(telegram_id: int) -> None:
    r = get_redis()
    key = f"disputes_open:{telegram_id}"
    r.incr(key)
    r.expire(key, 86400 * 7)  # 7-day window


def decrement_open_disputes(telegram_id: int) -> None:
    r = get_redis()
    key = f"disputes_open:{telegram_id}"
    current = r.get(key)
    if current and int(current) > 0:
        r.decr(key)


# ── Health check ──────────────────────────────────────────────────────────────

def check_redis_connection() -> bool:
    try:
        return get_redis().ping()
    except Exception as e:
        log.error("redis_connection_failed", error=str(e))
        return False
