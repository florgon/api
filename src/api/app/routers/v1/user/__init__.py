"""
    User API routers.
    
    Provides routers to work with users and etc.
"""

from fastapi import APIRouter

from . import user_security, user_profile, user_email_confirmation, user


def _get_router() -> APIRouter:
    """
    Returns prebuilt router for including above.
    """
    router = APIRouter(prefix="/user", tags=["user"])

    for module in [user, user_security, user_profile, user_email_confirmation]:
        router.include_router(module.router)

    return router


router = _get_router()

__all__: list[str] = []
