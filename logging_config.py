"""Structured logging configuration for the Hallucination-Free LLM Engine.

Replaces print() statements with proper logging infrastructure.

Usage:
    from logging_config import get_logger
    logger = get_logger(__name__)
    
    logger.info("Retrieved %d documents", count)
    logger.warning("Cache miss, rebuilding BM25 index")
    logger.error("Generation failed: %s", error)
"""

import logging
import logging.handlers
import os
from pathlib import Path
from config import ENVIRONMENT, LOG_LEVEL


# ============ LOG DIRECTORY SETUP ============

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "engine.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"


# ============ LOG FORMAT ============

CONSOLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ============ CONFIGURE ROOT LOGGER ============

def setup_logging():
    """Configure logging for the entire application."""
    
    # Set root logger level
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Console handler (colored output in development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if ENVIRONMENT == "development" else logging.INFO)
    console_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT, DATE_FORMAT))
    root_logger.addHandler(console_handler)
    
    # Rotating file handler (10MB max, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(FILE_FORMAT, DATE_FORMAT))
    root_logger.addHandler(file_handler)
    
    # Error file handler (errors only)
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(FILE_FORMAT, DATE_FORMAT))
    root_logger.addHandler(error_handler)
    
    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Configured logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("Processing query: %s", query)
    """
    return logging.getLogger(name)


# ============ PERFORMANCE LOGGING ============

class PerformanceLogger:
    """Context manager for timing operations."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.debug("Starting: %s", self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self.start_time
        if exc_type:
            self.logger.error("%s failed after %.2fs: %s", self.operation, elapsed, exc_val)
        else:
            self.logger.info("%s completed in %.2fs", self.operation, elapsed)
        return False


# ============ INITIALIZE ON IMPORT ============

# Set up logging when module is imported
_root_logger = setup_logging()
_root_logger.info("Logging initialized (environment=%s, level=%s)", ENVIRONMENT, LOG_LEVEL)
