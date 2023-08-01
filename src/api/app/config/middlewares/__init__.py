"""
    Custom middlewares.
    Provides interface for adding custom middlewares to the application.
    And middlewares itself.
"""

from fastapi import FastAPI

from .gatey import add_gatey_middleware
from .cors import add_cors_middleware
from .context import add_context_middleware


def add_middlewares(_app: FastAPI) -> None:
    """
    Registers all custom middlewares to the FastAPI application.
    """
    add_cors_middleware(_app)
    add_gatey_middleware(_app)
    add_context_middleware(_app)
