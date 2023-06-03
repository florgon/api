"""
    FastAPI v2 routers.
    
    Provides routers (API methods) for version 2.
"""

from fastapi import FastAPI

from . import user


def include_v2_routers(app: FastAPI) -> None:
    """
    Registers (including) FastAPI routers for FastAPI app.
    """
    modules = [user]
    for module in modules:
        app.include_router(module.router, prefix="v2")
