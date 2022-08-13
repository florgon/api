"""
    API version 1.
    Provides endpoints with logic for `v1` version of the API.

    FastAPI API routers.
"""

from fastapi import APIRouter
from . import (
    admin,
    blog,
    email,
    ext_oauth,
    gift,
    oauth,
    oauth_client,
    secure,
    security,
    session,
    upload,
    user,
    utils,
)


def get_api_routers() -> list[APIRouter]:
    """
    Returns FastAPI API routers for all endpoints.
    """
    modules = [
        oauth_client,
        email,
        session,
        oauth,
        user,
        utils,
        secure,
        ext_oauth,
        admin,
        security,
        upload,
        gift,
        blog,
    ]
    api_routers = map(lambda module: module.router, modules)
    return api_routers


__all__ = [
    "get_api_routers",
]
