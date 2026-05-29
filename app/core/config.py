from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Decision Engine API"
    version: str = "1.0.0"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/decision_engine"
    auto_create_schema: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
