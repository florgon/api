"""
    Cache (`fastapi_cache`) event handlers (startup connection).
"""
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache import FastAPICache
from app.services.cache import plain_cache_key_builder, JSONResponseCoder
from app.config import get_settings, get_logger


async def fastapi_cache_on_startup(_always_supress_disabled: bool = False) -> None:
    """
    Initalizes FastAPI cache (`fastapi_cache2` package).
    If server configured with disabled caching, it will automatically disable it and will be just boilerplate.
    Cache is used for requests / functions.
    """

    settings = get_settings()
    logger = get_logger()

    backend = None
    enabled = (
        settings.fastapi_cache_enable
        and not _always_supress_disabled
        and (settings.cache_dsn or settings.fastapi_cache_use_inmemory_backend)
    )

    if enabled:
        logger.info("[fastapi_cache] Initialising backend...")
        if settings.fastapi_cache_use_inmemory_backend:
            # `legacy` in memory backend that will just store plain cache data `as-is` in memory.
            # should not used in production or something like that as there is `redis` way.
            backend = InMemoryBackend()
            logger.warning(
                "[fastapi_cache] Successfully initialised `in-memory` backend which is not preferred, "
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
            logger.info("[fastapi_cache] Successfully initialised `redis` backend!")

    logger.info(
        "[fastapi_cache] Initialising cache singleton (enable=%s)..."
        if enabled
        else "[fastapi_cache] Skipping initialising cache singleton as disabled (enable=%s)",
        enabled,
    )
    FastAPICache.init(
        backend=backend,
        prefix="routes-caches",
        enable=settings.fastapi_cache_enable,
        # Defaults when not specified in decorator.
        coder=JSONResponseCoder,
        key_builder=plain_cache_key_builder,
        expire=None,
    )
    logger.info("[fastapi_cache] Finished startup event, cache installed!")
