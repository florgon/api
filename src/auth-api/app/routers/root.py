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


@router.get("/")
async def root() -> JSONResponse:
    """ Root page. """
    return api_success({
        "methods": [
            "/user",
            "/verify",
            "/signin",
            "/signup",
            "/changelog",
            "/email/"
        ]
    })


@router.get("/changelog")
async def changelog() -> JSONResponse:
    """ API changelog page. """
    return api_success(API_CHANGELOG)
