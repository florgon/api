"""
    Starlette context middleware register.
"""

from starlette_context.middleware import RawContextMiddleware
from starlette_context import plugins
from fastapi import FastAPI
from app.config import get_logger


def add_context_middleware(_app: FastAPI) -> None:
    """
    Registers context middleware to the FastAPI application.

    TODO: Settings.
    """

    _app.add_middleware(
        RawContextMiddleware,
        plugins=[
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin(),
        ],
    )
    get_logger().info("[context] Starlette context enabled and installed!")
