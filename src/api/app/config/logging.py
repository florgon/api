"""
    Logging configuration.
"""
from fastapi.logger import logger as fastapi_logger

from .environment.logging import get_logger


def hook_fastapi_logger() -> None:
    """
    Hooks logger with FastAPI.
    """
    logger = get_logger()
    fastapi_logger.handlers = logger.handlers
    fastapi_logger.setLevel(logger.level)
