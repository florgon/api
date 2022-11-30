"""
    FastAPI routers for application.
"""

from fastapi import FastAPI
from app.config import get_settings
from . import (
    admin,
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
    mailings,
)


def include_routers(app: FastAPI) -> None:
    """
    Registers (Including) FastAPI routers for FastAPI app.
    """
    proxy_url_prefix = get_settings().proxy_url_prefix
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
        mailings,
    ]:
        app.include_router(module.router, prefix=proxy_url_prefix)
