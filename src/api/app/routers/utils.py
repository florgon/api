"""
    Utils API router.
    Provides API methods (routes) for working some utils stuff.
"""

from time import time

from app.services.api.response import api_success
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/utils.getServerTime")
async def method_utils_get_server_time() -> JSONResponse:
    """Returns time at server in unix timestamp."""

    return api_success({"server_time": time()})


@router.get("/utils.ping")
async def method_utils_ping() -> JSONResponse:
    """Returns pong (as answer to ping)."""

    return api_success({"ping": "pong!"})
