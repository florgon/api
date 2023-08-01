"""
    Configuration settings (queried from environment variables).
    
    For more information read configuration documentation.
    (CONFIGURATION.md)
"""

# Weird stuff, but order here is important (and isort will not take into account your wishes)
from .settings import get_settings, Settings  # isort:skip
from .database import get_database_settings  # isort:skip
from .mail import get_mail_settings, get_mail  # isort:skip
from .logging import get_logging_settings, get_logger  # isort:skip
from .gatey import get_gatey_settings, get_gatey_client  # isort:skip
from .openapi import get_openapi_kwargs  # isort:skip

__all__ = [
    "get_database_settings",
    "get_mail_settings",
    "get_mail",
    "Settings",
    "get_settings",
    "get_logging_settings",
    "get_logger",
    "get_gatey_client",
    "get_gatey_settings",
    "get_openapi_kwargs",
]
