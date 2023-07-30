"""
    Utils API router.
    Provides API methods (routes) for working some utils stuff.
"""

from time import time

from fastapi.responses import JSONResponse
from fastapi import APIRouter
from app.services.api import api_success
from app.schemas.features import FeaturesModel

router = APIRouter(
    include_in_schema=True,
    tags=["utils"],
    prefix="/utils",
    default_response_class=JSONResponse,
)


@router.get("/status")
async def status() -> JSONResponse:
    """
    Returns API status alongside with time in unix timestamp on the server.
    """

    return api_success({"status": "OK", "server_time": time()})


@router.get("/features")
async def features() -> JSONResponse:
    """
    Returns API features (like, is there signup open or other stuff).
    May be used for displaying some service outage information.
    """

    return api_success(FeaturesModel.from_settings())
