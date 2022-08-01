"""
    Authentication server API routers.
    (FastAPI routers)
"""

from fastapi import FastAPI

from app.config import get_settings

from . import (admin, blog, email, ext_social_auth, gift, oauth, oauth_client,
               secure, security, session, upload, user, utils)


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
