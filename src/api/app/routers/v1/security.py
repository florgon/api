"""
    User security API router.
    Provides API methods (routes) for working with user security.
"""

from fastapi.responses import JSONResponse
from fastapi import Request, Depends, BackgroundTasks, APIRouter
from app.services.verification import decode_email_token
from app.services.validators.user import (
    validate_password_field,
    convert_email_to_standardized,
)
from app.services.tokens.email_token import EmailToken
from app.services.tfa import validate_user_tfa_otp_from_request, generate_tfa_otp
from app.services.request import (
    query_auth_data_from_request,
    AuthDataDependency,
    AuthData,
)
from app.services.permissions import Permission
from app.services.passwords import get_hashed_password, check_password
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success, api_error, ApiErrorCode
from app.serializers.session import serialize_sessions
from app.email import messages as email_messages
from app.database.repositories import UserSessionsRepository
from app.database.dependencies import get_repository, get_db, Session
from app.database import crud
from app.config import get_settings

router = APIRouter(tags=["security"], include_in_schema=False)


@router.get("/security.getInfo")
async def method_security_get_info(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns security information about current user."""
    user = query_auth_data_from_request(
        req, db, required_permissions={Permission.security}
    ).user
    return api_success(
        {
            "security": {
                "tfa": {
                    "enabled": user.security_tfa_enabled,
                    "can_enabled": user.is_verified,
                    "device_type": "email",
                }
            }
        }
    )


@router.get("/security.userEnableTfa")
async def method_security_user_enable_tfa(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Enables TFA for the current user."""
    query_auth_data_from_request(req, db, required_permissions={Permission.security})
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Security not implemented yet (2FA not implemented).",
    )


@router.get("/security.userDisableTfa")
async def method_security_user_disable_tfa(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Disables TFA for the current user."""
    query_auth_data_from_request(req, db, required_permissions={Permission.security})
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Security not implemented yet (2FA not implemented).",
    )


@router.get(
    "/security.userPasswordChangeRequestTfaOtp",
    dependencies=[Depends(RateLimiter(times=1, minutes=1))],
)
async def method_security_user_password_change_request_tfa_otp(
    req: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> JSONResponse:
    """Requests 2FA OTP to be send (if configured, or skip if not required)."""

    user = query_auth_data_from_request(
        req, db, required_permissions={Permission.security}
    ).user
    current_password = req.query_params.get("current_password")
    new_password = req.query_params.get("new_password")
    if not new_password or not current_password:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`current_password` and `new_password` is required.",
        )

    # Check password.
    validate_password_field(new_password)
    if not check_password(
        current_password, user.password, hash_method=user.security_hash_method  # type: ignore
    ):
        return api_error(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "Current password is not same with one that you passed!",
        )

    if not user.security_tfa_enabled:
        return api_error(
            ApiErrorCode.AUTH_TFA_NOT_ENABLED, "2FA not enabled for this account."
        )

    tfa_device = "email"  # Device type.
    tfa_otp_is_sent = False  # If false, OTP was not sent due no need.

    if tfa_device == "email":
        # Email 2FA device.
        # Send 2FA OTP to email address.

        # Generate key.
        tfa_otp = generate_tfa_otp(user, device_type=tfa_device)

        # Send OTP.
        email_messages.send_password_change_tfa_otp_email(
            background_tasks, user.email, user.get_mention(), tfa_otp  # type: ignore
        )
        tfa_otp_is_sent = True
    elif tfa_device == "mobile":
        # Mobile 2FA device.
        # No need to send 2FA OTP.
        # As mobile will automatically generate a new TOTP itself.
        tfa_otp_is_sent = False
    else:
        return api_error(ApiErrorCode.API_UNKNOWN_ERROR, "Unknown 2FA device!")

    return api_success({"tfa_device": tfa_device, "tfa_otp_is_sent": tfa_otp_is_sent})


@router.get(
    "/security.userChangePassword",
    dependencies=[Depends(RateLimiter(times=3, minutes=1))],
)
async def method_security_user_change_password(
    req: Request,
    background_tasks: BackgroundTasks,
    logout_foreign_sessions: bool = True,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Requests change password for the current user."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions={Permission.security}
    )
    user = auth_data.user
    current_password = req.query_params.get("current_password")
    new_password = req.query_params.get("new_password")
    if not new_password or not current_password:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`current_password` and `new_password` is required.",
        )

    # Check password and TFA.
    validate_user_tfa_otp_from_request(req, user)  # type: ignore
    validate_password_field(new_password)
    if check_password(
        current_password, user.password, hash_method=user.security_hash_method  # type: ignore
    ):
        return api_error(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "Password are the same!",
        )
    return api_error(
        ApiErrorCode.AUTH_INVALID_CREDENTIALS,
        "Current password is not same with one that you passed!",
    )


@router.get(
    "/security.userRequestResetPassword",
    dependencies=[Depends(RateLimiter(times=2, minutes=5))],
)
async def method_security_user_request_reset_password(
    background_tasks: BackgroundTasks,
    email: str,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Requests reset password within email."""

    user = crud.user.get_by_email(db, convert_email_to_standardized(email))
    payload = {
        "email": email,
    }
    if user is None:
        return api_success(payload)

    settings = get_settings()
    reset_otp = EmailToken(
        settings.security_tokens_issuer, settings.security_email_tokens_ttl, user.id  # type: ignore
    ).encode(
        key=user.password  # type: ignore
    )

    email_messages.send_password_reset_email(
        background_tasks, user.email, user.get_mention(), reset_otp  # type: ignore
    )
    return api_success(payload)


@router.get(
    "/security.userResetPassword",
    dependencies=[Depends(RateLimiter(times=2, minutes=5))],
)
async def method_security_user_reset_password(
    background_tasks: BackgroundTasks,
    email: str,
    reset_token: str,
    new_password: str,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Resets password from OTP sent for email before."""

    user = crud.user.get_by_email(db, convert_email_to_standardized(email))
    if user is None:
        return api_error(ApiErrorCode.API_FORBIDDEN, "Invalid values!")
    email_token = decode_email_token(reset_token, secret_key=user.password)  # type: ignore
    if email_token.get_subject() != user.id:
        return api_error(ApiErrorCode.API_FORBIDDEN, "Integrity error!")

    # Change password.
    user.password = get_hashed_password(new_password, hash_method=None)  # type: ignore[assignment]
    user.security_hash_method = 0  # type: ignore[assignment]
    db.commit()

    # Notifiy the user.
    email_messages.send_password_changed_notification_email(
        background_tasks, user.email, user.get_mention()  # type: ignore
    )

    # Logout from all devices except this.
    repo = UserSessionsRepository(db=db)
    repo.deactivate_list(repo.get_by_owner_id(owner_id=user.id, active_only=True))  # type: ignore
    return api_success({"password_is_changed": True, "sessions_was_closed": False})


@router.get(
    "/security.listSessions", dependencies=[Depends(RateLimiter(times=3, seconds=10))]
)
async def list_sessions(
    repo: UserSessionsRepository = Depends(get_repository(UserSessionsRepository)),
    auth_data: AuthData = Depends(
        AuthDataDependency(required_permissions={Permission.security})
    ),
) -> JSONResponse:
    """
    Lists all active sessions and return current session ID.
    TODO: Review vulnerabilities of that method.
    """
    sessions = repo.get_by_owner_id(auth_data.session.owner_id)  # type: ignore
    return api_success(
        {
            **serialize_sessions(sessions, db=repo.db),
            "current_id": auth_data.session.id,
        }
    )
