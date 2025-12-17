from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "My FastAPI Project"

    # Приклад URL: postgresql+asyncpg://user:password@localhost:5432/dbname
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str  # Можна задати значення за замовчуванням
    JWT_EXPIRATION_SECONDS: int


    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """
        Цей валідатор дозволяє передавати список у різних форматах.
        1. Як список (якщо налаштування беруться з python-коду).
        2. Як рядок JSON (з .env файлу).
        3. Як рядок через кому (на випадок, якщо JSON незручний).
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # default is False
        extra="ignore",
    )

settings = Settings()
