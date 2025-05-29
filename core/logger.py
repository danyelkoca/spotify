import logging
import time
import psutil
import os
from functools import wraps
from logging.handlers import RotatingFileHandler
import colorlog


class SpotifyLogger:
    _instance = None
    _logger = None
    _default_level = logging.INFO  # Set default to INFO

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance

    def set_level(self, level):
        """Set the logging level"""
        self._logger.setLevel(level)

    def _setup(self):
        """Setup logging configuration"""
        if self._logger is None:
            # Create logs directory if it doesn't exist
            log_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(log_dir, exist_ok=True)

            # Setup logger
            self._logger = logging.getLogger("spotify_assistant")
            self._logger.setLevel(self._default_level)  # Use default level

            # File handler with rotation (10MB max size, keep 5 backup files)
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, "spotify.log"),
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
            )

            # Console handler
            console_handler = logging.StreamHandler()

            # Create formatters and add them to the handlers
            # File formatter - no colors needed
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            # Console formatter with colors
            console_formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
                secondary_log_colors={},
                style="%",
            )

            file_handler.setFormatter(file_formatter)
            console_handler.setFormatter(console_formatter)

            # Add handlers to the logger
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

    @classmethod
    def get_logger(cls):
        """Get the logger instance"""
        if cls._instance is None:
            cls()
        return cls._instance._logger


def log_execution(func):
    """Decorator to log function execution and performance metrics"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = SpotifyLogger.get_logger()
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        # Log function entry
        logger.debug(f"Entering {func.__name__} with " f"args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)

            # Calculate metrics
            execution_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss
            memory_delta = end_memory - start_memory

            # Log success with metrics
            logger.info(
                f"Success: {func.__name__} completed in {execution_time:.2f}s, "
                f"memory delta: {memory_delta/1024/1024:.2f}MB"
            )

            return result

        except Exception as e:
            # Log failure with metrics
            execution_time = time.time() - start_time
            logger.error(
                f"Failed: {func.__name__} error after {execution_time:.2f}s: {str(e)}",
                exc_info=True,
            )
            raise

    return wrapper
