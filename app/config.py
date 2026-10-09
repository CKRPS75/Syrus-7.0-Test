import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TrustRoute API"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database URL default to postgresql+psycopg
    DATABASE_URL: str = "postgresql+psycopg://trustroute:password@localhost:5432/trustroute"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
