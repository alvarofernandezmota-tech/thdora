from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./thdora.db"
    TELEGRAM_BOT_TOKEN: str = Field(min_length=1)
    LLM_BACKEND: str = "groq"
    GROQ_API_KEY: str = Field(min_length=1)
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    ALLOWED_USERS: str = ""
    OWNER_TELEGRAM_ID: int = 0
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    GITHUB_TOKEN: str = Field(min_length=1)
    GITHUB_OWNER: str = "alvarofernandezmota-tech"
    GITHUB_REPO: str = "yggdrasil-dew"


settings = Settings()
