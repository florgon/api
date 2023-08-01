"""
    Logging configuraion (logger).
"""

from logging import getLogger, Logger
from functools import lru_cache

from pydantic import BaseSettings
from fastapi.logger import logger as fastapi_logger

# TODO: Research splitting logger names.


class LoggingSettings(BaseSettings):
    """
    Configuration for the logging logger.
    """

    name: str = "gunicorn.error"

    class Config:
        env_prefix = "LOGGING_"


@lru_cache(maxsize=1)
def get_logging_settings() -> LoggingSettings:
    return LoggingSettings()


@lru_cache(maxsize=1)
def get_logger() -> Logger:
    return getLogger(name=get_logging_settings().name)


def hook_fastapi_logger() -> None:
    logger = get_logger()
    fastapi_logger.handlers = logger.handlers
    fastapi_logger.setLevel(logger.level)
    logger.info("[core] Hooked logging successfully!")
