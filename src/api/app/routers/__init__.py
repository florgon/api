"""
    FastAPI routers for application.
"""

from fastapi import FastAPI

from .v2 import include_v2_routers
from .v1 import include_v1_routers


def include_routers(app: FastAPI) -> None:
    """
    Registers (Including) FastAPI routers for FastAPI app.
    """
    include_v1_routers(app=app)
    include_v2_routers(app=app)
