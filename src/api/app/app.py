"""
    FastAPI application, entry point.
"""

from fastapi import FastAPI

from .routers import include_routers
from .config.middlewares import add_middlewares
from .config import get_app_kwargs, DEPENDENCY_OVERRIDES


def create_application() -> FastAPI:
    """
    Create core FastAPI application with all setup.
    """
    app = FastAPI(**get_app_kwargs())
    app.dependency_overrides = DEPENDENCY_OVERRIDES

    add_middlewares(app)
    include_routers(app)

    return app
