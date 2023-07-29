"""
    FastAPI v1 routers.
    
    Provides routers (API methods) for version 1.
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
    mailings,
    gift,
    ext_oauth,
    email,
    admin,
)


def include_v1_routers(app: FastAPI) -> None:
    """
    Registers (including) FastAPI routers for FastAPI app.
    """
    modules = [
        oauth_client,
        email,
        session,
        oauth,
        user,
        utils,
        tokens,
        ext_oauth,
        admin,
        user_security,
        gift,
        mailings,
        tickets,
    ]
    for module in modules:
        app.include_router(module.router, prefix="/v1")
