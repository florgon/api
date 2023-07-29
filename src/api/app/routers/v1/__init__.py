"""
    FastAPI v1 routers.
    
    Provides routers for API version 1.
"""

from fastapi import FastAPI

from . import (
    utils,
    user_security,
    user,
    tokens,
    tickets,
    session,
    oauth_client,
    oauth,
    email,
)


def include_v1_routers(_app: FastAPI) -> None:
    """
    Includes FastAPI routers onto the app.
    """
    for module in [
        oauth_client,
        email,
        session,
        oauth,
        user,
        utils,
        tokens,
        user_security,
        tickets,
    ]:
        _app.include_router(module.router, prefix="/v1")
