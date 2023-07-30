"""
    Custom event handlers.
    Provides interface for adding custom event handlers to the application
    and event handlers itself.
"""

from fastapi import FastAPI
from app.services import limiter

from .prometheus import prometheus_metrics_on_startup


def add_event_handlers(_app: FastAPI) -> None:
    """
    Registers all custom event handlers to the FastAPI application.
    """

    # Limiter.
    _app.add_event_handler("startup", limiter.on_startup)
    _app.add_event_handler("shutdown", limiter.on_shutdown)

    # Prometheus.
    _app.add_event_handler("startup", prometheus_metrics_on_startup(_app))
