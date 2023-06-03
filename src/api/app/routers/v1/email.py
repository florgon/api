"""
    Email confirmation API router.
    Provides API methods (routes) for working with email confirmation.
"""


# import urllib.parse

from fastapi.responses import JSONResponse
from fastapi import Request, Depends, BackgroundTasks, APIRouter
from app.services.verification import generate_confirmation_link, decode_email_token
from app.services.request import query_auth_data_from_request
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success, api_error
from app.services.api.errors import ApiErrorCode
from app.email import messages
from app.database.dependencies import get_db, Session
from app.database import crud

router = APIRouter(include_in_schema=False)


@router.get(
    "/_emailConfirmation.confirm",
    dependencies=[Depends(RateLimiter(times=3, seconds=1))],
)
async def method_email_confirmation_confirm(
    cft: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Confirms email from given CFT (Confirmation token).
    :param cft: Confirmation token from email.
    """
    # Validating CFT, grabbing email from CFT payload.
    email_token = decode_email_token(token=cft)

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
    messages.send_verification_end_email(
        background_tasks, user.email, user.get_mention()
    )
    return api_success({"email": user.email, "is_confirmed": True})


@router.get("/_emailConfirmation.resend")
async def method_email_confirmation_resend(
    req: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Resends email confirmation to user email address."""
    user = query_auth_data_from_request(req, db).user
    if user.is_verified:
        return api_error(
            ApiErrorCode.EMAIL_CONFIRMATION_ALREADY_CONFIRMED,
            "Confirmation not required. You already confirmed your email!",
        )
    await RateLimiter(times=2, hours=1).check(req)

    messages.send_verification_email(
        background_tasks,
        email=user.email,
        mention=user.get_mention(),
        confirmation_link=generate_confirmation_link(user.id),
    )
    return api_success({"email": user.email})
