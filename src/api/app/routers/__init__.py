"""
    Authentication server API routers.
    (FastAPI routers)
"""

from fastapi import FastAPI

from app.config import get_settings

from . import email, oauth_client, secure, oauth, session, user, utils, ext_social_auth, admin


def register_routers(app: FastAPI) -> None:
    """
    Registers (Including) FastAPI routers for FastAPI app.
    """
    for router in [
        oauth_client.router,
        email.router,
        session.router,
        oauth.router,
        user.router,
        utils.router,
        secure.router,
        ext_social_auth.router,
        admin.router,
    ]:
        app.include_router(router, prefix=get_settings().proxy_url_prefix)
