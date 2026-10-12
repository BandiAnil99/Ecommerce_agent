from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    DATABASE_URL: str = "sqlite:///./shopping.db"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    MAX_RECOMMENDATIONS: int = 5
    CORS_ORIGINS: str = "*"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def app_root(self) -> Path:
        return Path(__file__).resolve().parent.parent


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
