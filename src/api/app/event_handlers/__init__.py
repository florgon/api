"""
    Custom middlewares.
    Provides interface for adding custom middlewares to the application.
    And middlewares itself.
"""

from fastapi import FastAPI

from app.services import limiter


def add_event_handlers(app: FastAPI) -> None:
    """
    Registers (add) all custom event handlers to the FastAPI application.
    """
    app.add_event_handler("startup", limiter.on_startup)
    app.add_event_handler("shutdown", limiter.on_shutdown)
