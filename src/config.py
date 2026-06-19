"""Configuración centralizada de THDORA usando pydantic-settings."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos
    DATABASE_URL: str = "sqlite:///./thdora.db"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(min_length=1)

    # LLM backend
    LLM_BACKEND: str = "groq"
    GROQ_API_KEY: str = Field(min_length=1)
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"

    # Sprint 5/6 — multi-nivel LLM
    ADMIN_TOKEN: str = ""
    OLLAMA_MODEL_LEVEL1: str = "qwen2.5:3b-instruct"
    OLLAMA_MODEL_LEVEL2: str = "llama3.2:3b"

    # Control de acceso
    ALLOWED_USERS: str = ""
    OWNER_TELEGRAM_ID: int = 0

    # API FastAPI interna
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    THDORA_API_URL: str = "http://localhost:8001"

    # Logging
    LOG_LEVEL: str = "INFO"

    # GitHub Contents API — yggdrasil-dew
    # Opcional: si no está configurado, /diario no funciona pero el bot arranca
    GITHUB_TOKEN: str = ""
    GITHUB_OWNER: str = "alvarofernandezmota-tech"
    GITHUB_REPO: str = "yggdrasil-dew"

    # OpenWeatherMap
    OWM_API_KEY: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Devuelve la instancia singleton de Settings.

    Uso correcto (lazy, testeable):
        from src.config import get_settings
        settings = get_settings()

    En tests, invalida la caché con:
        get_settings.cache_clear()
    """
    return Settings()


# Alias de compatibilidad — NO instancia al importar
# Usar get_settings() en código nuevo
def _get_settings_compat() -> Settings:
    return get_settings()


# DEPRECADO: acceso directo. Migrar a get_settings()
# Mantenido solo para no romper imports existentes durante la migración
class _LazySettings:
    """Proxy lazy que no instancia Settings hasta el primer acceso."""
    _instance: Settings | None = None

    def __getattr__(self, name: str):
        if self._instance is None:
            self._instance = get_settings()
        return getattr(self._instance, name)


settings = _LazySettings()
