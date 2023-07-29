"""
    OAuth API routers.
    
    Provides routers to work with OAuth (Clients, workflow).
"""

from fastapi import APIRouter

from . import oauth_client, oauth


def _get_router() -> APIRouter:
    """
    Returns prebuilt router for including above.
    """
    router = APIRouter(prefix="/oauth", tags=["oauth"])

    for module in [oauth, oauth_client]:
        router.include_router(module.router)

    return router


router = _get_router()

__all__: list[str] = []
