"""
    Auth API root routers.
"""

# Libraries.
from fastapi import APIRouter

# Services.
from services.api.response import api_success

# Fast API router.
router = APIRouter(prefix="")

@router.get("/")
async def root():
    """ Root page. """
    return api_success({
        "methods": [
            "/user",
            "/signin",
            "/signup",
            "/changelog"
        ]
    })

@router.get("/changelog")
async def changelog():
    """ API changelog page. """
    return api_success({
        "versions": {
            "1.0": {
                "1.0": [
                    "Initial release.",
                ]
            }
        }
    })