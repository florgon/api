"""
    Gatey middleware register.
"""

from gatey_sdk.integrations.starlette import GateyStarletteMiddleware
from fastapi import FastAPI
from app.config import get_settings, get_logger, get_gatey_client


def add_gatey_middleware(_app: FastAPI) -> None:
    """
    Registers Gatey logging middleware to the FastAPI application.

    Used for logging integration of the Gatey inside FastAPI (starlette) application.
    """

    settings = get_settings()

    if not settings.gatey_is_enabled:
        get_logger().warning("[gatey] Gatey is disabled! Skipping adding middleware!")
        return
    if get_gatey_client() is None:
        get_logger().warning(
            "[gatey] Gatey client is None! Skipping adding middleware!"
        )
        return

    async def _pre_capture_hook(*_) -> None:
        get_logger().info("[gatey] Got captured exception! Sending to Gatey client...")

    _app.add_middleware(
        GateyStarletteMiddleware,
        client=None,
        client_getter=get_gatey_client,
        pre_capture_hook=_pre_capture_hook,
        capture_requests_info=settings.gatey_capture_requests_info,
        capture_reraise_after=True,
    )
    get_logger().info("[gatey] Gatey is enabled and installed as middleware!")
