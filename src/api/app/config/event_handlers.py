"""
    Custom FastAPI event handlers.
    Provides list of handlers.
"""

from app.services import limiter
from app.database.bootstrap import dispose_database, bootstrap_database

from .logging import hook_fastapi_logger

STARTUP_HANDLERS = [hook_fastapi_logger, limiter.on_startup, bootstrap_database]
SHUTDOWN_HANDLERS = [limiter.on_shutdown, dispose_database]
