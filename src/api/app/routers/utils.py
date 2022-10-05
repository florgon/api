"""
    Utils API router.
    Provides API methods (routes) for working some utils stuff.
"""

from time import time

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.config import get_gatey_client
from app.services.api.response import api_success

router = APIRouter()


@router.get("/utils.getServerTime")
async def method_utils_get_server_time() -> JSONResponse:
    """Returns time at server in unix timestamp."""

    return api_success({"server_time": time()})


@router.get("/utils.ping")
async def method_utils_ping() -> JSONResponse:
    """Returns pong (as answer to ping)."""

    return api_success({"ping": "pong!"})


@router.get("/utils.raiseISE")
async def method_raise_ise() -> JSONResponse:
    """Raises internal server error that should trigger Gatey (or some checks out of the server)."""

    try:
        return api_success({"division_by_zero": 1 / 0})
    except Exception as e:
        get_gatey_client().capture_exception(e)
        raise e
