"""
    Custom middlewares.
    Provides interface for adding custom middlewares to the application.
    And middlewares itself.
"""

from fastapi import FastAPI

try:
    from prometheus_fastapi_instrumentator import Instrumentator

    prometheus_instrumentator_installed = True
except ImportError:
    prometheus_instrumentator_installed = False

from app.config import get_settings, get_logger
from app.services import limiter


def add_event_handlers(app: FastAPI) -> None:
    """
    Registers (add) all custom event handlers to the FastAPI application.
    """
    app.add_event_handler("startup", limiter.on_startup)
    app.add_event_handler("shutdown", limiter.on_shutdown)
    if get_settings().prometheus_metrics_exposed:
        if prometheus_instrumentator_installed:
            app.add_event_handler(
                "startup",
                lambda: Instrumentator().instrument(app).expose(app),
            )
        else:
            get_logger().warn(
                "You are enabled `prometheus_metrics_exposed` but `prometheus_fastapi_instrumentator` is not installed in system!"
            )
