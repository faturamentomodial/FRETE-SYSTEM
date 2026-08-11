from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "frete-system"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://frete:frete@localhost:5432/frete"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    N8N_BASE_URL: str = "http://n8n:5678"

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Timeouts de integração (segundos), conforme definido no Sprint 1
    TIMEOUT_API_INTEGRACAO: int = 15
    TIMEOUT_BROWSER_INTEGRACAO: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
