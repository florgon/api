"""
    Custom middlewares.
    Provides interface for adding custom middlewares to the application.
    And middlewares itself.
"""

from fastapi import FastAPI

from app.services import limiter
from app.event_handlers.cache import fastapi_cache_on_startup
from app.event_handlers.prometheus import prometheus_metrics_on_startup


def add_event_handlers(_app: FastAPI) -> None:
    """
    Registers (add) all custom event handlers to the FastAPI application.
    """

    # Cache.
    _app.add_event_handler("startup", fastapi_cache_on_startup)

    # Limiter.
    _app.add_event_handler("startup", limiter.on_startup)
    _app.add_event_handler("shutdown", limiter.on_shutdown)

    # Prometheus.
    _prometheus_metrics_startup_event = prometheus_metrics_on_startup(_app)
    if _prometheus_metrics_startup_event:
        _app.add_event_handler("startup", _prometheus_metrics_startup_event)
