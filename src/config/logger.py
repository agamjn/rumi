"""
Centralized logging configuration for Rumi.

Provides console logging for local development and CloudWatch integration for production.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Optional log level override (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance

    Example:
        >>> from src.config.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process", extra={"source": "blog"})
    """
    logger = logging.getLogger(name)

    # Set level from parameter or default to INFO
    log_level = level or "INFO"
    logger.setLevel(getattr(logging, log_level.upper()))

    # Only add handler if none exists (avoid duplicate logs)
    if not logger.handlers:
        # Console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, log_level.upper()))

        # Format: timestamp - name - level - message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# TODO: Add CloudWatch integration for production (Task 0.3)
# Will use watchtower library to stream logs to CloudWatch when ENVIRONMENT=production
