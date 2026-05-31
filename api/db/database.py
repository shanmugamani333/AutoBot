"""
Database connection — SQLAlchemy engine and session factory.
Every module imports get_db() to get a session.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from api.config import settings
import structlog

log = structlog.get_logger()

# ── Engine ───────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # detect stale connections
    pool_size=10,
    max_overflow=20,
    echo=settings.APP_ENV == "development",
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ── Dependency (FastAPI) ─────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency — yields a DB session and closes it after the request.

    Usage in routes:
        @router.get("/products")
        def list_products(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Health check ─────────────────────────────────────────────────────────────
def check_db_connection() -> bool:
    """Ping the DB — used by the /health endpoint."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        log.error("db_connection_failed", error=str(e))
        return False


# ── Enable pgvector extension ─────────────────────────────────────────────────
def enable_pgvector() -> None:
    """
    Run once on startup to ensure the pgvector extension is active.
    The pgvector/pgvector Docker image includes it; we just need to enable it.
    """
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.commit()
    log.info("pgvector_enabled")
