from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Decision Engine API"
    version: str = "1.0.0"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/decision_engine"

    class Config:
        env_file = ".env"


settings = Settings()
