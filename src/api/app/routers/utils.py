"""
    Utils API router.
    Provides API methods (routes) for working some utils stuff.
"""

from time import time

from app.config import get_settings
from app.services.api.response import api_success
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["utils"])


@router.get("/utils.getServerTime")
async def method_utils_get_server_time() -> JSONResponse:
    """Returns time at server in unix timestamp."""

    return api_success({"server_time": time()})


@router.get("/utils.getFeatures")
async def method_utils_get_features() -> JSONResponse:
    """Returns features from the backend."""

    settings = get_settings()
    return api_success(
        {
            "features": {
                "auth": {
                    "auth_signup_is_open": settings.signup_open_registration,
                },
                "service": {
                    "is_under_maintenance": settings.service_is_under_maintenance,
                    "is_under_debug_environment": settings.is_under_debug_environment,
                },
                "openapi": {
                    "enabled": settings.openapi_enabled,
                    "urls": [
                        settings.openapi_url,
                        settings.openapi_docs_url,
                        settings.openapi_redoc_url,
                    ]
                    if settings.openapi_enabled
                    else [],
                },
            }
        }
    )
