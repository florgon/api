"""
    Cache utils for the `fastapi-cache2` library.

    There is stuff like special coders / key builders.
    Please look at library docs to get more information.
"""

from .key_builders import (
    authenticated_cache_key_builder,
    device_cache_key_builder,
    plain_cache_key_builder,
)
from .coders import JSONResponseCoder

__all__ = [
    "authenticated_cache_key_builder",
    "device_cache_key_builder",
    "plain_cache_key_builder",
    "JSONResponseCoder",
]
