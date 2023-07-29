"""
    FastAPI routers for application.
"""

from fastapi import FastAPI

from .v1 import include_v1_routers


def include_routers(_app: FastAPI) -> None:
    """
    Includes FastAPI routers onto the app.
    """
    include_v1_routers(_app=_app)
