"""
    Token API routers.
"""

# Libraries.
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

# Services.
from app import services
from app.services import serializers
from app.services.api.response import api_success

# Other.
from app import database
from app.database import crud
from app.config import (
    Settings, get_settings
)

# Database dependency.
get_db = database.dependencies.get_db

# Fast API router.
router = APIRouter()


@router.get("/user")
async def user(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    """ Returns user information by token. """

    # Try authenticate.
    is_authenticated, token_payload_or_error, _ = services.request.try_decode_token_from_request(req, settings.jwt_secret)
    if not is_authenticated:
        return token_payload_or_error
    token_payload = token_payload_or_error

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])
    return api_success(serializers.user.serialize(user))


@router.get("/verify")
async def verify(req: Request, settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Returns is given token valid (not expired, have valid signature) or not and information about it. """

    # Try authenticate.
    is_authenticated, token_payload_or_error, _ = services.request.try_decode_token_from_request(req, settings.jwt_secret)
    if not is_authenticated:
        return token_payload_or_error
    token_payload = token_payload_or_error

    # All ok.
    return api_success({
        "token": {
            "subject": token_payload["sub"],
            "issuer": token_payload["iss"],
            "issued_at": token_payload["iat"],
            "expires_at": token_payload["exp"],
            "user": {
                "username": token_payload["_user"]["username"],
            }
        }
    })
