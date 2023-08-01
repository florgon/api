"""
    Logging configuraion (logger).
"""

from logging import getLogger, Logger
from functools import lru_cache

from pydantic import BaseSettings

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
