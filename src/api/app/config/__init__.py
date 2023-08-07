"""
    Configuration stuff (Environment settings, hooks).
"""


from .environment import *


def get_app_kwargs() -> dict:
    """
    Returns FastAPI kwargs.
    """
    from .exceptions import EXCEPTION_HANDLERS
    from .event_handlers import STARTUP_HANDLERS, SHUTDOWN_HANDLERS

    return {
        "debug": get_settings().is_development,
        "on_startup": STARTUP_HANDLERS,
        "on_shutdown": SHUTDOWN_HANDLERS,
        "exception_handlers": EXCEPTION_HANDLERS,
        **get_openapi_kwargs(),
    }


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
    "get_app_kwargs",
]
