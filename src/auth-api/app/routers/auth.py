"""
    Auth API auth routers.
"""

# Libraries.
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

# Services.
from app import services
from app.services import serializers
from app.services.api.errors import ApiErrorCode
from app.services.api.response import (
    api_error,
    api_success
)

# Other.
from app import database
from app.database import crud
from app.email import messages
from app.config import (
    Settings, get_settings
)

# Database dependency.
get_db = database.dependencies.get_db

# Fast API router.
router = APIRouter()


@router.get("/signup")
async def signup(username: str, email: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ API endpoint to signup and create new user. """

    # Try validate request for fields.
    is_valid, validation_error = services.validators.user.validate_signup_fields(db, username, email, password)
    if not is_valid:
        return validation_error

    # Create new user.
    password = services.passwords.get_hashed_password(password)
    user = crud.user.create(db=db, email=email, username=username, password=password)
    token = services.jwt.encode(user, settings.jwt_issuer, settings.jwt_ttl, settings.jwt_secret)

    # Send email.
    if settings.send_confirmation_email_on_signup:
        confirmation_link = services.cftokens.generate_confirmation_token(user.email, settings.cft_secret, settings.cft_salt, settings.proxy_url_host, settings.proxy_url_prefix)
        await messages.send_verification_email(user.email, user.username, confirmation_link)

    # Return user with token.
    return api_success({
        **serializers.user.serialize(user),
        "token": token
    })


@router.get("/signin")
async def signin(login: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ API endpoint to signin and get token. """

    # Query user.
    user = crud.user.get_by_login(db=db, login=login)

    # Check credentials.
    if not user or not services.passwords.check_password(password=password, hashed_password=user.password):
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid credentials")

    # Generate token.
    token = services.jwt.encode(user, settings.jwt_issuer, settings.jwt_ttl, settings.jwt_secret)

    # Return user with token.
    return api_success({
        **serializers.user.serialize(user),
        "token": token
    })
