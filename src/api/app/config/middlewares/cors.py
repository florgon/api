"""
    CORS middleware register.
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.config import get_settings, get_logger


def add_cors_middleware(_app: FastAPI) -> None:
    """
    Registers CORS middleware to the FastAPI application.

    By default, API should be allowed for CORS,
    as any application can be allowed to make requests.

    May be disabled by `cors_enabled` config setting.
    """

    settings = get_settings()
    if not settings.cors_enabled:
        get_logger().warning("[cors] CORS is disabled! Please notice that!")
        return

    _app.add_middleware(
        CORSMiddleware,
        allow_credentials=settings.cors_allow_credentials,
        allow_origins=settings.cors_allow_origins,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        max_age=settings.cors_max_age,
    )
    get_logger().info("[cors] CORS enabled and installed!")
