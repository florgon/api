"""
    Authentication server API routers.
    (FastAPI routers)
"""

from app.config import get_settings
from fastapi import FastAPI

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


def include_routers(app: FastAPI) -> None:
    """
    Registers (Including) FastAPI routers for FastAPI app.
    """
    settings = get_settings()
    proxy_url_prefix = settings.proxy_url_prefix
    for module in [
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
    ]:
        app.include_router(module.router, prefix=proxy_url_prefix)
