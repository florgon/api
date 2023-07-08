"""
    Cache (`fastapi_cache`) event handlers (startup connection).
"""
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends import Backend
from fastapi_cache import FastAPICache
from app.services.cache import plain_cache_key_builder, JSONResponseCoder
from app.config import get_settings, get_logger


async def fastapi_cache_on_startup() -> None:
    """
    Initalizes FastAPI cache (`fastapi_cache2` package).
    If server configured with disabled caching, it will automatically disable it and will be just boilerplate.
    Cache is used for requests / functions.
    TODO: More configuration with server configuration.
    """

    logger = get_logger()
    enabled = _cache_is_enabled()
    backend = _get_cache_backend() if enabled else None

    logger.info(
        f"[cache] {'Initialising cache singleton' if enabled else 'Skipping initialising cache singleton as disabled'}"
    )

    FastAPICache.init(
        backend=backend,
        prefix="routes-caches",
        enable=get_settings().fastapi_cache_enable,
        # Defaults when not specified in decorator.
        coder=JSONResponseCoder,
        key_builder=plain_cache_key_builder,
        expire=None,
    )
    logger.info("[cache] Finished startup event, cache installed!")


def _get_cache_backend() -> Backend:
    """
    Builds a cache backend based on the settings.
    """

    logger = get_logger()
    settings = get_settings()

    logger.info("[cache] Initialising backend...")
    if settings.fastapi_cache_use_inmemory_backend:
        # `legacy` in memory backend that will just store plain cache data `as-is` in memory.
        # should not used in production or something like that as there is `redis` way.
        backend = InMemoryBackend()
        logger.warning(
            "[cache] Successfully initialised `in-memory` backend which is not preferred, "
            "please look into `redis` backend with disabling `fastapi_cache_use_inmemory_backend`!"
        )
    else:
        # Base `redis` backend when cache data stored inside `redis`.
        redis = aioredis.from_url(
            url=settings.cache_dsn,
            encoding=settings.cache_encoding,
            decode_responses=True,
        )
        backend = RedisBackend(redis)
        logger.info("[cache] Successfully initialised `redis` backend!")

    return backend


def _cache_is_enabled() -> bool:
    """
    Is cache should be installed as configured with settings.
    """
    settings = get_settings()
    return settings.fastapi_cache_enable and (
        settings.cache_dsn is not None or settings.fastapi_cache_use_inmemory_backend
    )
