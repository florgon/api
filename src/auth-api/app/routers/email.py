"""
    Auth API auth routers.
"""

# Libraries.
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

# Services.
from app import services
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


@router.get("/email")
async def email_root() -> JSONResponse:
    """ Email root page. """
    return api_success({
        "methods": [
            "/email/confirm",
            "/email/resend_confirmation",
        ]
    })


@router.get("/email/confirm")
async def email_confirm(cft: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ API endpoint to confirm email. """

    # Confirm token.
    is_valid, token_payload = services.cftokens.confirm(cft, settings.cft_max_age, settings.cft_secret, settings.cft_salt)
    if not is_valid:
        return api_error(ApiErrorCode.CFT_INVALID_TOKEN, "Invalid confirmation token, try resend confirmation.")
    email = token_payload

    # Get user by email from token.
    user = crud.user.get_by_email(db=db, email=email)
    if not user:
        return api_error(ApiErrorCode.CFT_EMAIL_NOT_FOUND, "Invalid confirmation token, user with this email was not found. ")

    # Do not confirm if already confirmed.
    if user.is_verified:
        return api_error(ApiErrorCode.CFT_EMAIL_ALREADY_CONFIRMED, "You already confirmed your email!")
        
    # Confirm.
    crud.user.email_confirm(db, user)

    return api_success({
        "email": email,
        "message": "Email confirmed!"
    })


@router.get("/email/resend_confirmation")
async def email_resend_confirmation(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ API endpoint to resend confirmation email. """

    # Try authetnicate.
    is_authenticated, token_payload_or_error, _ = services.request.try_decode_token_from_request(req, settings.jwt_secret)
    if not is_authenticated:
        return token_payload_or_error
    token_payload = token_payload_or_error

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])

    # Do not send if already confirmed.
    if user.is_verified:
        return api_error(ApiErrorCode.CFT_EMAIL_ALREADY_CONFIRMED, "You already confirmed your email!")
        
    # Send email.
    confirmation_link = services.cftokens.generate_confirmation_token(user.email, settings.cft_secret, settings.cft_salt, settings.proxy_url_host, settings.proxy_url_prefix)
    await messages.send_verification_email(user.email, user.email, confirmation_link)

    # Return OK.
    return api_success({
        "message": "Email confirmation resended!"
    })