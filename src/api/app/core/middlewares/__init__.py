"""
    Custom middlewares.
    Provides interface for adding custom middlewares to the application.
    And middlewares itself.
"""

from app.core.config import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def add_middlewares(app: FastAPI) -> None:
    """
    Registers (add) all custom middlewares to the FastAPI application.
    """
    _add_cors_middleware(app)


def _add_cors_middleware(app: FastAPI) -> None:
    """
    Registers CORS middleware to the FastAPI application.

    By default, API should be allowed for CORS,
    as any application can be allowed to make requests.

    May be disabled by `cors_enabled` config setting.
    """
    settings = get_settings()
    if not settings.cors_enabled:
        return

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=settings.cors_allow_credentials,
        allow_origins=settings.cors_allow_origins,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        max_age=settings.cors_max_age,
    )
