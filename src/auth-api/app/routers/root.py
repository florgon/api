"""
    Auth API root routers.
"""

# Libraries.
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Services.
from app.services.api.response import api_success

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
            "/changelog"
        ]
    })

@router.get("/changelog")
async def changelog() -> JSONResponse:
    """ API changelog page. """
    return api_success({
        "versions": {
            "1.0": {
                "1.0": [
                    "Initial release.",
                ],
                "1.0.1": [
                    "Allowed CORS requests."
                ],
                "1.0.2": [
                    "New `/verify` method that returns is given token valid or not and decoded information about token.",
                    "Email notification when new user sign up (Email notification events may be changed without notice here)"
                ],
                "1.0.3": [
                    "Tokens now includes `_user` and `username`"
                ],
            }
        }
    })