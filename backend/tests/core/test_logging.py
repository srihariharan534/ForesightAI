import logging
from unittest.mock import patch
from app.core.logging import setup_logging
from app.core.config import settings

def test_setup_logging_development() -> None:
    """Test logging setup in development environment."""
    with patch("app.core.config.settings.ENVIRONMENT", "development"):
        setup_logging()
        logger = logging.getLogger()
        
        # Verify handler was added
        assert len(logger.handlers) >= 1
        
        # In dev, we should be using standard formatter, not JSON formatter
        formatter = logger.handlers[0].formatter
        assert isinstance(formatter, logging.Formatter)
        
def test_setup_logging_production() -> None:
    """Test logging setup in production environment."""
    with patch("app.core.config.settings.ENVIRONMENT", "production"):
        setup_logging()
        logger = logging.getLogger()
        
        # Verify handler was added
        assert len(logger.handlers) >= 1
        
        # In prod, we should be using JSON formatter
        formatter = logger.handlers[0].formatter
        from pythonjsonlogger.jsonlogger import JsonFormatter
        assert isinstance(formatter, JsonFormatter)
