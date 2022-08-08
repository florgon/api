"""
    Email confirmation API router.
    Provides API methods (routes) for working with email confirmation.
"""


import urllib.parse

from app.config import Settings, get_settings
from app.database import crud
from app.database.dependencies import Session, get_db
from app.email import messages
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success
from app.services.limiter.depends import RateLimiter
from app.services.request import query_auth_data_from_request
from app.tokens import EmailToken
from app.tokens.exceptions import (
    TokenExpiredError,
    TokenInvalidError,
    TokenInvalidSignatureError,
    TokenWrongTypeError,
)
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse

router = APIRouter()


# TODO: Allow specify URL for email confirmation.


@router.get(
    "/_emailConfirmation.confirm",
    dependencies=[Depends(RateLimiter(times=3, seconds=1))],
)
async def method_email_confirmation_confirm(
    cft: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Confirms email from given CFT (Confirmation token)."""

    # Validating CFT, grabbing email from CFT payload.
    try:
        email_token = EmailToken.decode(cft, key=settings.security_email_tokens_ttl)
    except (TokenInvalidError, TokenInvalidSignatureError):
        return api_error(
            ApiErrorCode.EMAIL_CONFIRMATION_TOKEN_INVALID,
            "Confirmation token not valid, mostly due to corrupted link. Try resend confirmation again.",
        )
    except TokenExpiredError:
        return api_error(
            ApiErrorCode.EMAIL_CONFIRMATION_TOKEN_INVALID,
            "Confirmation token expired. Try resend confirmation again.",
        )
    except TokenWrongTypeError:
        return api_error(
            ApiErrorCode.EMAIL_CONFIRMATION_TOKEN_INVALID,
            "Expected token to be a confirmation token, not another type of token.",
        )

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=email_token.get_subject())
    if not user:
        return api_error(
            ApiErrorCode.EMAIL_CONFIRMATION_USER_NOT_FOUND,
            "Confirmation token has been issued for email, that does not refers to any existing user! "
            "Did you updated your account email address?",
        )
    if user.is_verified:
        return api_error(
            ApiErrorCode.EMAIL_CONFIRMATION_ALREADY_CONFIRMED,
            "Confirmation not required. You already confirmed your email!",
        )

    crud.user.email_confirm(db, user)
    await messages.send_verification_end_email(
        background_tasks, user.email, user.get_mention()
    )
    return api_success({"email": user.email, "is_confirmed": True})


@router.get("/_emailConfirmation.resend")
async def method_email_confirmation_resend(
    req: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Resents email confirmation to user email address."""
    auth_data = query_auth_data_from_request(req, db)
    user = auth_data.user

    if user.is_verified:
        return api_error(
            ApiErrorCode.EMAIL_CONFIRMATION_ALREADY_CONFIRMED,
            "Confirmation not required. You already confirmed your email!",
        )
    await RateLimiter(times=2, hours=1).check(req)

    # TBD: Refactor this.
    email = user.email
    confirmation_token = EmailToken(
        settings.security_tokens_issuer, settings.security_email_tokens_ttl, user.id
    ).encode(key=settings.security_email_tokens_secret_key)
    # confirmation_link = urllib.parse.urljoin(
    #    settings.proxy_url_domain,
    #    settings.proxy_url_prefix + "/_emailConfirmation.confirm",
    # )
    confirmation_link = "https://florgon.space/email/verify"
    email_confirmation_link = f"{confirmation_link}?cft={confirmation_token}"
    await messages.send_verification_email(
        background_tasks, email, user.get_mention(), email_confirmation_link
    )

    return api_success({"email": email})
