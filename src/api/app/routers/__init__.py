"""
    Authentication server API routers.
    (FastAPI routers)
"""

from fastapi import FastAPI

from app.config import get_settings

from . import (
    email,
    oauth_client,
    secure,
    oauth,
    session,
    user,
    utils,
    ext_social_auth,
    admin,
    security,
    upload,
    gift,
    blog,
)


def register_routers(app: FastAPI) -> None:
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
        ext_social_auth,
        admin,
        security,
        upload,
        gift,
        blog,
    ]:
        app.include_router(module.router, prefix=proxy_url_prefix)
