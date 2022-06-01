"""
    Email confirmation API router.
    Provides API methods (routes) for working with email confirmation.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.services.request import query_auth_data_from_request
from app.services.cftokens import confirm_cft, generate_confirmation_link
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success
from app.services.limiter.depends import RateLimiter

from app.database.dependencies import get_db, Session
from app.database import crud
from app.email import messages
from app.config import get_settings, Settings


router = APIRouter()


# TODO: Allow specify URL for email confirmation.


@router.get("/_emailConfirmation.confirm")
async def method_email_confirmation_confirm(cft: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Confirms email from given CFT (Confirmation token). """

    # Validating CFT, grabbing email from CFT payload.
    is_valid, token_payload = confirm_cft(cft, settings.cft_max_age, settings.cft_secret, settings.cft_salt)
    if not is_valid:
        return api_error(ApiErrorCode.EMAIL_CONFIRMATION_TOKEN_INVALID, "Confirmation token not valid, mostly due to corrupted link. Try resend confirmation again.")
    email = token_payload

    # Query user.
    user = crud.user.get_by_email(db=db, email=email)
    if not user:
        return api_error(ApiErrorCode.EMAIL_CONFIRMATION_USER_NOT_FOUND, "Confirmation token has been issued for email, that does not refers to any existing user! Did you updated your account email address?")
    if user.is_verified:
        return api_error(ApiErrorCode.EMAIL_CONFIRMATION_ALREADY_CONFIRMED, "Confirmation not required. You already confirmed your email!")
        
    crud.user.email_confirm(db, user)
    return api_success({
        "email": email,
        "confirmed": True
    })


@router.get("/_emailConfirmation.resend", dependencies=[Depends(RateLimiter(hours=1))])
async def method_email_confirmation_resend(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Resends email confirmation to user email address. """
    auth_data = query_auth_data_from_request(req, db)
    user = auth_data.user
    
    if user.is_verified:
        return api_error(ApiErrorCode.EMAIL_CONFIRMATION_ALREADY_CONFIRMED, "Confirmation not required. You already confirmed your email!")

    email = user.email
    email_confirmation_link = generate_confirmation_link(email, settings.cft_secret, settings.cft_salt, settings.proxy_url_host, settings.proxy_url_prefix)
    await messages.send_verification_email(email, user.username, email_confirmation_link)

    return api_success({
        "email": email
    })