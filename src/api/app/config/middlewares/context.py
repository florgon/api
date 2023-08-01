"""
    Starlette context middleware hook.
"""

from starlette_context.middleware import RawContextMiddleware
from starlette_context import plugins
from fastapi import FastAPI


def add_context_middleware(_app: FastAPI) -> None:
    """Registers context middleware to the FastAPI application."""
    # TODO: Configuration.
    _app.add_middleware(
        RawContextMiddleware,
        plugins=[
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin(),
        ],
    )
