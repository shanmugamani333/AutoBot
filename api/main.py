import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.config import get_settings
from api.db.session import init_db
from api.routes import webhook, health

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("starting_store_bot_api", env=settings.app_env)
    await init_db()
    yield
    # Shutdown
    logger.info("shutting_down_store_bot_api")


app = FastAPI(
    title="Autonomous Store Bot API",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(webhook.router, tags=["webhook"])
