from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.
    """

    PROJECT_NAME: str = "ForesightAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v

    # ==========================
    # DATABASE (SQLite)
    # ==========================
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./foresight.db"

    # Authentication
    SECRET_KEY: str = "SUPER_SECRET_KEY_REPLACE_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # MLflow
    MLFLOW_TRACKING_URI: str = "sqlite:///mlflow.db"

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
    }


settings = Settings()