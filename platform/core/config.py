from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "THDORA Agent Platform"
    app_version: str = "2.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://thdora:thdora@localhost:5432/thdora_platform"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_agent_cache_ttl: int = 300  # 5 minutos

    # LLM — Groq (producción) o Ollama (local)
    groq_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama-3.3-70b-versatile"

    # Telegram
    telegram_bot_token: str = ""

    # Security
    secret_key: str = "changeme-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # LangSmith (observabilidad, opcional)
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "thdora-platform"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
