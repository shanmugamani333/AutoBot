from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Telegram
    telegram_bot_token: str = "placeholder"
    telegram_webhook_url: str = ""

    # Database
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "storebot"
    postgres_user: str = "storebot"
    postgres_password: str = "changeme"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Ollama
    ollama_base_url: str = "http://ollama:11434"
    ollama_llm_model: str = "mistral"
    ollama_vision_model: str = "llava"
    ollama_embed_model: str = "nomic-embed-text"

    # App
    app_env: str = "development"
    app_secret_key: str = "changeme"
    log_level: str = "INFO"

    # Guardrails
    scope_filter_min_score: float = 0.30
    confidence_min_score: float = 0.70

    # Session
    session_ttl_seconds: int = 1800
    session_max_turns: int = 5

    # Rate limits
    rate_limit_messages_per_min: int = 10
    rate_limit_max_open_disputes: int = 3

    # Loyalty
    loyalty_points_rate: float = 0.05
    points_cache_ttl_seconds: int = 600

    # Admin
    admin_telegram_chat_id: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
