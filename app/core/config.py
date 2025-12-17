from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "My FastAPI Project"

    # Приклад URL: postgresql+asyncpg://user:password@localhost:5432/dbname
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # default is False
    )


settings = Settings()
