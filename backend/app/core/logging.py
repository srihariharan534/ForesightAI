import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger
from app.core.config import settings

def setup_logging() -> None:
    """
    Configure application logging.
    Uses structured JSON logging for production environments and standard
    formatting for development to aid in readability.
    """
    logger = logging.getLogger()
    
    # Set log level based on config
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger.setLevel(log_level)

    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Define formatter based on environment
    if settings.ENVIRONMENT == "production":
        # Structured JSON logging for production (CloudWatch, ELK, etc.)
        formatter: Any = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        # Standard logging for local development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Prevent UVicorn access logs from double logging
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = True
