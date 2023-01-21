"""
    User security API router.
    Provides API methods (routes) for working with user security.
"""

from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from app.database.dependencies import Session, get_db
from app.services.api.response import ApiErrorCode, api_error, api_success
from app.services.permissions import Permission
from app.services.request import query_auth_data_from_request
from app.services.passwords import check_password, get_hashed_password
from app.services.validators.user import validate_password_field
from app.email import messages as email_messages
from app.services.tfa import validate_user_tfa_otp_from_request, generate_tfa_otp
from app.services.limiter.depends import RateLimiter
from app.database import crud

router = APIRouter(tags=["security"], include_in_schema=False)


@router.get("/security.getInfo")
async def method_security_get_info(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns security information about current user."""
    user = query_auth_data_from_request(
        req, db, required_permissions=[Permission.security]
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
    query_auth_data_from_request(req, db, required_permissions=[Permission.security])
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Security not implemented yet (2FA not implemented).",
    )


@router.get("/security.userDisableTfa")
async def method_security_user_disable_tfa(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Disables TFA for the current user."""
    query_auth_data_from_request(req, db, required_permissions=[Permission.security])
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
        req, db, required_permissions=[Permission.security]
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
    if not check_password(current_password, user.password, user.security_hash_method):
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
            background_tasks, user.email, user.get_mention(), tfa_otp
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
    logout_foreign_sessions: bool = True,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Requests change password for the current user."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.security]
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
    validate_user_tfa_otp_from_request(req, user)
    validate_password_field(new_password)
    passwords_is_same = check_password(
        current_password, user.password, user.security_hash_method
    )
    if passwords_is_same:
        return api_error(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "Password are the same!",
        )
    if not passwords_is_same:
        return api_error(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "Current password is not same with one that you passed!",
        )

    # Change password.
    user.password = get_hashed_password(new_password, hash_method=None)
    user.security_hash_method = 0
    db.commit()

    # Logout from all devices except this.
    if logout_foreign_sessions:
        sessions = crud.user_session.get_active_by_owner_id(db, owner_id=user.id)
        if auth_data.token.get_type() == "access":
            # Just to be sure.
            current_session_id = auth_data.token.get_session_id()
            sessions = list(
                filter(lambda session: session.id != current_session_id, sessions)
            )
        crud.user_session.deactivate_list(db, sessions)

    return api_success(
        {"password_is_changed": True, "sessions_was_closed": logout_foreign_sessions}
    )
