"""
    User email API router.
    Provides methods for working with email confirmation.
"""

from fastapi.responses import JSONResponse
from fastapi import Depends, BackgroundTasks, APIRouter
from app.services.verification import decode_email_token
from app.services.request import AuthDataDependency, AuthData
from app.services.permissions import Permission
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success, api_error
from app.services.api.errors import ApiErrorCode
from app.email import messages
from app.database.dependencies import get_db, Session
from app.database import crud

router = APIRouter(prefix="/email/confirmation", tags=["email"])


@router.post("/finish")
async def finish_confirmation(
    email_token: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Finish email confirmation process by checking confirmation token from the email.
    """
    user = crud.user.get_by_id(db, decode_email_token(email_token).get_subject())
    if not user or user.is_verified:
        return api_error(
            ApiErrorCode.EMAIL_CONFIRMATION_USER_NOT_FOUND,
            "User is already confirmed or changed email address",
        )

    crud.user.email_confirm(db, user)
    messages.send_verification_end_email(background_tasks, user)

    return api_success({})


@router.post("/request", dependencies=[Depends(RateLimiter(times=2, hours=1))])
async def request_confirmation(
    background_tasks: BackgroundTasks,
    auth_data: AuthData = Depends(
        AuthDataDependency(
            required_permissions={Permission.email}, allow_not_confirmed=True
        )
    ),
) -> JSONResponse:
    """
    Requests confirmation email to be sent to the user email.
    """
    messages.send_verification_email(background_tasks, auth_data.user)
    return api_success({"email": auth_data.user.email})
