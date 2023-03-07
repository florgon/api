"""
    Utils API router.
    Provides API methods (routes) for working some utils stuff.
"""

from time import time

from fastapi.responses import JSONResponse
from fastapi import APIRouter

from app.services.api.response import api_success

router = APIRouter(tags=["utils"])


@router.get("/utils.getServerTime")
async def method_utils_get_server_time() -> JSONResponse:
    """Returns time at server in unix timestamp."""

    return api_success({"server_time": time()})
