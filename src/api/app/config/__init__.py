"""
    Configuration stuff (Environment settings, etc).
    
    For more information read configuration documentation.
    (CONFIGURATION.md)
"""

# Weird stuff, but order here is important (and isort will not take into account your wishes)
from .settings import get_settings, Settings  # isort:skip
from .database import get_database_settings, DatabaseSettings  # isort:skip
from .mail import get_mail_settings, MailSettings, get_mail  # isort:skip
from .logging import get_logging_settings, get_logger, LoggingSettings  # isort:skip
from .gatey import get_gatey_client, get_gatey_settings, GateySettings  # isort:skip
from .openapi import get_openapi_kwargs  # isort:skip

__all__ = [
    "DatabaseSettings",
    "get_database_settings",
    "MailSettings",
    "get_mail_settings",
    "get_mail",
    "Settings",
    "get_settings",
    "LoggingSettings",
    "get_logging_settings",
    "get_logger",
    "GateySettings",
    "get_gatey_client",
    "get_gatey_settings",
    "get_openapi_kwargs",
]
