from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "local"
    log_level: str = "INFO"

    anthropic_api_key: str = ""

    database_url: str = "postgresql+psycopg://user:password@localhost:5432/jipmunseo"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "policy_documents"


@lru_cache
def get_settings() -> Settings:
    return Settings()
