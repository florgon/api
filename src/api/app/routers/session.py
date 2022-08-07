"""
    Authentication session API router.
    Provides API methods (routes) for working with session (Signin, signup).
    For external authorization (obtaining `access_token`, not `session_token`) see OAuth.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Header, Request
from fastapi.responses import JSONResponse
from pyotp import TOTP

from app.config import Settings, get_settings
from app.database import crud
from app.database.dependencies import Session, get_db
from app.email import messages as email_messages
from app.serializers.session import serialize_sessions
from app.serializers.user import serialize_user
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success
from app.services.limiter.depends import RateLimiter
from app.services.permissions import Permission
from app.services.request import (
    query_auth_data_from_request,
)
from app.services.validators.user import validate_signin_fields, validate_signup_fields
from app.services.session import publish_new_session_with_token

router = APIRouter()


@router.get("/_session._getUserInfo")
async def method_session_get_user_info(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns user account information by session token, and additional information about token."""
    auth_data = query_auth_data_from_request(req, db, only_session_token=True)
    return api_success(
        {
            **serialize_user(
                auth_data.user,
                include_email=False,
                include_optional_fields=True,
                include_private_fields=True,
                include_profile_fields=False,
            ),
            "siat": auth_data.token.get_issued_at(),
            "sexp": auth_data.token.get_expires_at(),
        }
    )


@router.get("/_session._signup", dependencies=[Depends(RateLimiter(times=3, hours=12))])
async def method_session_signup(
    req: Request,
    username: str,
    email: str,
    password: str,
    user_agent: str = Header(""),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """API endpoint to signup and create new user."""
    if not settings.signup_open_registration:
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "User signup closed (Registration forbidden by server administrator)",
        )

    validate_signup_fields(db, username, email, password)
    user = crud.user.create(db=db, email=email, username=username, password=password)
    token, session = publish_new_session_with_token(
        user=user, user_agent=user_agent, db=db, req=req
    )
    return api_success(
        {
            **serialize_user(user),
            "session_token": token.encode(key=session.token_secret),
            "sid": session.id,
        }
    )


@router.get("/_session._logout")
async def method_session_logout(
    req: Request, revoke_all: bool = False, sid: int = 0, db: Session = Depends(get_db)
) -> JSONResponse:
    """Logout user over session (or over all sessions, or specific sessions)."""
    auth_data = query_auth_data_from_request(req, db, only_session_token=True)
    await RateLimiter(times=1, seconds=15).check(req)

    if revoke_all:
        sessions = crud.user_session.get_active_by_owner_id(
            db, owner_id=auth_data.user.id
        )
        crud.user_session.deactivate_list(db, sessions)
        return api_success({"sids": [_session.id for _session in sessions]})

    session = crud.user_session.get_by_id(db, sid) if sid else auth_data.session
    if not session or not session.is_active:
        return api_error(
            ApiErrorCode.API_ITEM_NOT_FOUND, "Session not found or already closed!"
        )

    crud.user_session.deactivate_one(db, session)
    return api_success({"sid": session.id})


@router.get("/_session._list", dependencies=[Depends(RateLimiter(times=3, seconds=10))])
async def method_session_list(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns list of all active sessions."""
    # This is weird, _session method allowed with only access token,
    # And also seems to expose private session information.
    auth_data = query_auth_data_from_request(
        req, db, only_session_token=False, required_permissions=[Permission.sessions]
    )
    current_session = auth_data.session
    sessions = crud.user_session.get_active_by_owner_id(db, current_session.owner_id)
    return api_success(
        {
            **serialize_sessions(sessions, db=db),
            "current_id": current_session.id,
        }
    )


@router.get(
    "/_session._requestTfaOtp", dependencies=[Depends(RateLimiter(times=1, minutes=1))]
)
async def method_session_request_tfa_otp(
    login: str,
    password: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Requests 2FA OTP to be send (if configured, or skip if not required)."""

    # Check credentials.
    user = crud.user.get_by_login(db=db, login=login)
    validate_signin_fields(user=user, password=password)

    if not user.security_tfa_enabled:
        return api_error(
            ApiErrorCode.AUTH_TFA_NOT_ENABLED, "2FA not enabled for this account."
        )

    tfa_device = "email"  # Device type.
    tfa_otp_is_sent = False  # If false, OTP was not sent due no need.

    if tfa_device == "email":
        # Email 2FA device.
        # Send 2FA OTP to email address.

        # Get generator.
        otp_secret_key = user.security_tfa_secret_key
        otp_interval = settings.security_tfa_totp_interval_email
        totp = TOTP(s=otp_secret_key, interval=otp_interval)

        # Get OTP.
        tfa_otp = totp.now()

        # Send OTP.
        await email_messages.send_tfa_otp_email(
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
    "/_session._signin", dependencies=[Depends(RateLimiter(times=3, seconds=5))]
)
async def method_session_signin(
    req: Request,
    login: str,
    password: str,
    user_agent: str = Header(""),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Authenticates user and gives new session token for user."""

    # Check credentials.
    user = crud.user.get_by_login(db=db, login=login)
    validate_signin_fields(user=user, password=password)

    if user.security_tfa_enabled:
        # If user has enabled 2FA.

        # Request 2FA OTP, raise error with continue information.
        tfa_otp = req.query_params.get("tfa_otp")
        if not tfa_otp:
            return api_error(
                ApiErrorCode.AUTH_TFA_OTP_REQUIRED,
                "2FA authentication one time password required!",
                {"tfa_otp_required": True},
            )

        tfa_device = "email"  # Device type.

        # Get OTP generator.
        otp_secret_key = user.security_tfa_secret_key
        otp_interval = (
            settings.security_tfa_totp_interval_email
            if tfa_device == "email"
            else settings.security_tfa_totp_interval_mobile
        )
        totp = TOTP(s=otp_secret_key, interval=otp_interval)

        # If OTP is not valid, raise error.
        if not totp.verify(tfa_otp):
            return api_error(
                ApiErrorCode.AUTH_TFA_OTP_INVALID,
                "2FA authentication one time password expired or invalid!",
            )

    token, session = publish_new_session_with_token(
        user=user, user_agent=user_agent, db=db, req=req
    )
    return api_success(
        {
            **serialize_user(user),
            "session_token": token.encode(key=session.token_secret),
            "sid": session.id,
        }
    )
