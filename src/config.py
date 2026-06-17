"""Configuración centralizada de THDORA usando pydantic-settings.

Todas las variables de entorno se leen desde aquí.
Importar `settings` para acceder a cualquier valor de configuración.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos
    DATABASE_URL: str = "sqlite:///./thdora.db"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(min_length=1)

    # LLM backend (groq | ollama)
    LLM_BACKEND: str = "groq"
    GROQ_API_KEY: str = Field(min_length=1)
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"

    # Control de acceso
    ALLOWED_USERS: str = ""
    OWNER_TELEGRAM_ID: int = 0

    # API FastAPI interna
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    THDORA_API_URL: str = "http://localhost:8001"  # URL para el bot (Docker: http://api:8000)

    # Logging
    LOG_LEVEL: str = "INFO"

    # GitHub Contents API — yggdrasil-dew
    GITHUB_TOKEN: str = Field(min_length=1)
    GITHUB_OWNER: str = "alvarofernandezmota-tech"
    GITHUB_REPO: str = "yggdrasil-dew"


settings = Settings()
