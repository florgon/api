"""
    Custom middlewares.
    Provides interface for adding custom middlewares to the application.
    And middlewares itself.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings


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

    ToDo (03.06.22): Add more configuration to the CORS (Custom origins and more).
    """
    if not get_settings().cors_enabled:
        return

    # For now,
    # CORS middleware exposes all,
    # later there is maybe some configuration to modify behavior.
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
