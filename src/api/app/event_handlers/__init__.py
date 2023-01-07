"""
    Custom middlewares.
    Provides interface for adding custom middlewares to the application.
    And middlewares itself.
"""

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.services.cache import JSONResponseCoder, plain_cache_key_builder

try:
    from prometheus_fastapi_instrumentator import Instrumentator

    prometheus_instrumentator_installed = True
except ImportError:
    prometheus_instrumentator_installed = False

from app.config import get_settings, get_logger
from app.services import limiter


def add_event_handlers(app: FastAPI) -> None:
    """
    Registers (add) all custom event handlers to the FastAPI application.
    """
    app.add_event_handler("startup", limiter.on_startup)
    app.add_event_handler("shutdown", limiter.on_shutdown)
    app.add_event_handler("startup", fastapi_cache_on_startup)
    if get_settings().prometheus_metrics_exposed:
        if prometheus_instrumentator_installed:
            app.add_event_handler(
                "startup",
                lambda: Instrumentator().instrument(app).expose(app),
            )
        else:
            get_logger().warn(
                "You are enabled `prometheus_metrics_exposed` but `prometheus_fastapi_instrumentator` is not installed in system!"
            )


async def fastapi_cache_on_startup() -> None:
    """
    Initalizes FastAPI cache.
    """

    settings = get_settings()
    redis = aioredis.from_url(
        url=settings.cache_dsn,
        encoding=settings.cache_encoding,
        decode_responses=True,
    )
    FastAPICache.init(
        backend=RedisBackend(redis),
        prefix="routes-caches",
        expire=None,
        coder=JSONResponseCoder,
        key_builder=plain_cache_key_builder,
        enable=True,
    )
