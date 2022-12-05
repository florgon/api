"""
    Custom middlewares.
    Provides interface for adding custom middlewares to the application.
    And middlewares itself.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gatey_sdk.integrations.starlette import GateyStarletteMiddleware
from app.config import get_settings, get_gatey_client, get_logger


def add_middlewares(app: FastAPI) -> None:
    """
    Registers (add) all custom middlewares to the FastAPI application.
    """
    _add_cors_middleware(app)
    _add_gatey_middleware(app)


def _add_gatey_middleware(app: FastAPI) -> None:
    """
    Registers Gatey logging middleware.
    """

    settings = get_settings()
    if not settings.gatey_is_enabled or get_gatey_client() is None:
        get_logger().info(
            "Gatey is not enabled or client is None! Skipping adding middleware!"
        )
        return

    async def _pre_capture_hook(*_):
        get_logger().info("Got captured Gatey exception! Sending to Gatey client...")

    app.add_middleware(
        GateyStarletteMiddleware,
        client=None,
        client_getter=get_gatey_client,
        pre_capture_hook=_pre_capture_hook,
        capture_requests_info=True,
        capture_reraise_after=True,
    )


def _add_cors_middleware(app: FastAPI) -> None:
    """
    Registers CORS middleware to the FastAPI application.

    By default, API should be allowed for CORS,
    as any application can be allowed to make requests.

    May be disabled by `cors_enabled` config setting.
    """
    settings = get_settings()
    if not settings.cors_enabled:
        get_logger().info("CORS is not enabled! Please notice that!")
        return

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=settings.cors_allow_credentials,
        allow_origins=settings.cors_allow_origins,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        max_age=settings.cors_max_age,
    )
