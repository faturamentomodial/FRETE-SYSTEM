from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "FreteWay API"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://frete:frete@localhost:5432/frete"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    N8N_BASE_URL: str = "http://n8n:5678"

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Consulta cadastral de CNPJ. O provedor pode ser trocado sem alterar o frontend.
    CNPJ_CONSULTA_BASE_URL: str = "https://brasilapi.com.br/api/cnpj/v1"
    CNPJ_CONSULTA_TIMEOUT_SECONDS: int = 10

    # Documentos originais das tabelas de frete.
    TABELA_FRETE_STORAGE_DIR: str = "storage/tabelas_frete"
    TABELA_FRETE_UPLOAD_MAX_BYTES: int = 25 * 1024 * 1024
    EMPRESA_LOGO_STORAGE_DIR: str = "storage/configuracoes/logos"
    EMPRESA_LOGO_MAX_BYTES: int = 2 * 1024 * 1024

    # Timeouts de integração (segundos), conforme definido no Sprint 1
    TIMEOUT_API_INTEGRACAO: int = 15
    TIMEOUT_BROWSER_INTEGRACAO: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
