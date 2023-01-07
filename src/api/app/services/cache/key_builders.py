"""
    Key builders that are used to build unique specific keys for the storage.

    By default `fastapi-cache2` only handles params and some code specific location.
    That is not useful for authorized routes.
"""

from hashlib import md5
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response

from fastapi_cache import FastAPICache

from app.services.request import get_token_from_request, get_client_host_from_request


def authenticated_cache_key_builder(
    func: Callable,
    namespace: str | None = "",
    request: Request | None = None,
    response: Response | None = None,
    args: tuple | None = None,
    kwargs: dict | None = None,
) -> str:
    """
    Key builder for routes that has auth.
    Uses token for caching.
    """

    # Identification of the authenticated user by token.
    access_token = (
        get_token_from_request(req=request, only_session_token=False) if request else ""
    )

    # Build key.
    additional_cached_tags = [access_token]
    return _cache_key_builder_internal_cacher(
        additional_cached_tags, func, namespace, request, response, args, kwargs
    )


def device_cache_key_builder(
    func: Callable,
    namespace: str | None = "",
    request: Request | None = None,
    response: Response | None = None,
    args: tuple | None = None,
    kwargs: dict | None = None,
) -> str:
    """
    Key builder for routes that has auth.
    Uses token for caching.
    """

    # Identification.
    client_host = get_client_host_from_request(request) if request else ""
    user_agent = request.headers.get("User-Agent", "") if request else ""

    additional_cached_tags = [user_agent, client_host]
    return _cache_key_builder_internal_cacher(
        additional_cached_tags, func, namespace, request, response, args, kwargs
    )


def _cache_key_builder_internal_cacher(
    additional_cached_tags: list[str],
    func: Callable,
    namespace: str | None = "",
    request: Request | None = None,
    response: Response | None = None,
    args: tuple | None = None,
    kwargs: dict | None = None,
) -> str:
    """
    Cache key builder base. Used for DRY.
    """
    # Remove parameters that always have different value (id) as located in different memory locations.
    # TODO: Research better solution.
    for param in ("db", "req", "background"):
        kwargs.pop(param, None)

    # Build cache key.
    cache_keys_prefix = f"{FastAPICache.get_prefix()}:{namespace}:"
    cache_key_func_call_signature = f"{func.__module__}:{func.__name__}:{args}:{kwargs}"
    cache_key_hash = md5(
        f"{cache_key_func_call_signature}:{':'.join(additional_cached_tags)}".encode()
    )  # nosec:B303

    # Cache key for storage.
    cache_key = cache_keys_prefix + cache_key_hash.hexdigest()
    return cache_key
