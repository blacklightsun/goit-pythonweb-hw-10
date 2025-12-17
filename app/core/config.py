from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "My FastAPI Project"

    # Приклад URL: postgresql+asyncpg://user:password@localhost:5432/dbname
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str  # Можна задати значення за замовчуванням
    JWT_EXPIRATION_SECONDS: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # default is False
        extra="ignore",
    )


settings = Settings()
