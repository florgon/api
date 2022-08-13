"""
    API version 1.
    Provides endpoints with logic for `v2` version of the API.

    FastAPI API routers.
"""

from fastapi import APIRouter


def get_api_routers() -> list[APIRouter]:
    """
    Returns FastAPI API routers for all endpoints.
    """
    modules = []
    api_routers = map(lambda module: module.router, modules)
    return api_routers


__all__ = [
    "get_api_routers",
]
