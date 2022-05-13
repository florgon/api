"""
    Auth API root routers.
"""

# Libraries.
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Services.
from app.services.api.response import api_success
from app.services.api.version import API_CHANGELOG

# Fast API router.
router = APIRouter(prefix="")


@router.get("/changelog")
async def changelog() -> JSONResponse:
    """ API changelog page. """
    return api_success(API_CHANGELOG)
