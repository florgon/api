"""
    Custom middlewares.
    Provides interface for adding custom middlewares to the application.
    And middlewares itself.
"""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.services import limiter


def add_event_handlers(app: FastAPI) -> None:
    """
    Registers (add) all custom event handlers to the FastAPI application.
    """
    app.add_event_handler("startup", limiter.on_startup)
    app.add_event_handler("shutdown", limiter.on_shutdown)
    if get_settings().prometheus_metrics_exposed:
        app.add_event_handler(
            "startup",
            lambda: Instrumentator()
            .instrument(app)
            .expose(app, endpoint=f"{get_settings().proxy_url_prefix}/metrics"),
        )
