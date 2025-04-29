"""
Logging module for the application.
Provides structured logging functionality using Loguru.
"""
from loguru import logger
import sys
import os
from datetime import datetime
from ..config import settings

# Configure main logger
logger.remove()  # Remove default handlers

# Console handler for development
if settings.DEBUG:
    logger.add(
        sys.stderr, 
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

# File handler for all logs (INFO and above)
log_file = settings.LOG_DIR / f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
logger.add(
    log_file,
    rotation="1 day",
    retention="30 days",
    level="INFO", # Log INFO level and above to the file
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message} | {extra}"
)

# Optionally, add a separate file handler for errors
error_log_file = settings.LOG_DIR / f"error_{datetime.now().strftime('%Y-%m-%d')}.log"
logger.add(
    error_log_file,
    level="ERROR",
    rotation="1 week",
    retention="1 month",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

class AppLogger:
    """Application logger wrapper for easy access."""
    
    @staticmethod
    def info(message: str, **kwargs):
        """Log info level message."""
        logger.info(message, **kwargs)
    
    @staticmethod
    def error(message: str, **kwargs):
        """Log error level message."""
        logger.error(message, **kwargs)
    
    @staticmethod
    def debug(message: str, **kwargs):
        """Log debug level message."""
        logger.debug(message, **kwargs)
    
    @staticmethod
    def warning(message: str, **kwargs):
        """Log warning level message."""
        logger.warning(message, **kwargs)
    
    @staticmethod
    def critical(message: str, **kwargs):
        """Log critical level message."""
        logger.critical(message, **kwargs)

# Create app logger instance for use in other modules
app_logger = AppLogger()
