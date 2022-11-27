"""
    Custom middlewares.
    Provides interface for adding custom middlewares to the application.
    And middlewares itself.
"""

from starlette.types import ASGIApp, Receive, Scope, Send
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, get_gatey_client, get_logger


class GateyMiddleware:
    """Gatey (error) logging middleware."""

    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            gatey_client = get_gatey_client()
            if gatey_client:
                get_logger().info(
                    "Got captured Gatey exception! Sending to Gatey client..."
                )
                get_gatey_client().capture_exception(e)
            raise e
        return


def add_middlewares(app: FastAPI) -> None:
    """
    Registers (add) all custom middlewares to the FastAPI application.
    """
    _add_gatey_middleware(app)
    _add_cors_middleware(app)


def _add_gatey_middleware(app: FastAPI) -> None:
    """
    Registers Gatey logging middleware.
    """
    app.add_middleware(GateyMiddleware)


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
