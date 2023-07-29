"""
    FastAPI v1 routers.
    
    Provides routers for API version 1.
"""

from fastapi import FastAPI, APIRouter

from . import utils, user, tokens, tickets, session, oauth


def include_v1_routers(_app: FastAPI) -> None:
    """
    Includes FastAPI routers onto the app.
    """

    router = APIRouter(prefix="/v1")
    for module in [session, oauth, utils, tokens, tickets, user]:
        router.include_router(
            module.router,
        )
    _app.include_router(router)
