"""
    Gatey middleware register.
"""

from gatey_sdk.integrations.starlette import GateyStarletteMiddleware
from fastapi import FastAPI
from app.config.logging import get_logger
from app.config import get_gatey_settings, get_gatey_client


def add_gatey_middleware(_app: FastAPI) -> None:
    """
    Registers Gatey logging middleware to the FastAPI application.

    Used for logging integration of the Gatey inside FastAPI (starlette) application.
    """

    settings = get_gatey_settings()

    if not settings.is_configured:
        get_logger().warning(
            "[gatey] Gatey is not configuring! Skipping adding middleware!"
        )
        return

    async def _pre_capture_hook(*_) -> None:
        get_logger().info("[gatey] Got captured exception! Sending to Gatey client...")

    _app.add_middleware(
        GateyStarletteMiddleware,
        client=None,
        client_getter=get_gatey_client,
        pre_capture_hook=_pre_capture_hook,
        capture_requests_info=settings.capture_requests_info,
        capture_reraise_after=True,
    )
    get_logger().info("[gatey] Gatey is configured and installed as middleware!")
