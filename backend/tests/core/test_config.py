import os
from unittest import mock
import pytest
from app.core.config import Settings

def test_settings_default_values() -> None:
    """Test that default configuration values are set correctly."""
    settings = Settings()
    assert settings.PROJECT_NAME == "ForesightAI"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.ENVIRONMENT == "development"
    assert settings.DEBUG is True

@mock.patch.dict(os.environ, {"POSTGRES_SERVER": "db-server", "POSTGRES_DB": "testdb"})
def test_settings_db_uri_generation() -> None:
    """Test that the SQLAlchemy URI is properly assembled from components."""
    settings = Settings()
    assert "postgresql://postgres:postgres@db-server:5432/testdb" in settings.SQLALCHEMY_DATABASE_URI

def test_cors_origins_parsing() -> None:
    """Test CORS origin string parsing."""
    settings = Settings(BACKEND_CORS_ORIGINS="http://localhost:3000, http://localhost:8080")
    origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    assert "http://localhost:3000/" in origins
    assert "http://localhost:8080/" in origins
