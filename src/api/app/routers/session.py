"""
    Authentication session API router.
    Provides API methods (routes) for working with session (Signin, signup).
    For external authorization (obtaining `access_token`, not `session_token`) see OAuth.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Header, Request
from fastapi.responses import JSONResponse
from app.database.repositories import UsersRepository
from app.database.dependencies import get_repository

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
    AuthDataDependency,
    AuthData,
)

from app.services.validators.user import (
    validate_signin_fields,
    validate_signup_fields,
    convert_email_to_standardized,
)
from app.services.session import publish_new_session_with_token
from app.services.tfa import validate_user_tfa_otp_from_request, generate_tfa_otp

router = APIRouter()


@router.get("/_session._getUserInfo")
async def method_session_get_user_info(
    auth_data: AuthData = Depends(AuthDataDependency(only_session_token=True)),
) -> JSONResponse:
    """Returns user account information by session token, and additional information about token."""
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


@router.post(
    "/_session._signup", dependencies=[Depends(RateLimiter(times=3, hours=12))]
)
async def method_session_signup(
    req: Request,
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

    body_json = await req.json()
    if (
        "username" not in body_json
        or "email" not in body_json
        or "password" not in body_json
    ):
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`username`, `email` and `password` fields are required!",
        )
    username, email, password = (
        body_json.get("username"),
        body_json.get("email"),
        body_json.get("password"),
    )
    # Used for email where domain like `ya.ru` is same with `yandex.ru` or `yandex.com`
    email = convert_email_to_standardized(email)

    validate_signup_fields(db, username, email, password)
    user = crud.user.create(db=db, email=email, username=username, password=password)
    if not user:
        return api_error(
            ApiErrorCode.API_TRY_AGAIN_LATER,
            "Unable to create account at this time, please try again later.",
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


@router.get("/_session._logout")
async def method_session_logout(
    req: Request,
    revoke_all: bool = False,
    sid: int = 0,
    db: Session = Depends(get_db),
    auth_data: AuthData = Depends(AuthDataDependency(only_session_token=True)),
) -> JSONResponse:
    """Logout user over session (or over all sessions, or specific sessions)."""
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
    db: Session = Depends(get_db),
    auth_data: AuthData = Depends(
        AuthDataDependency(
            only_session_token=False, required_permissions=[Permission.sessions]
        )
    ),
) -> JSONResponse:
    """Returns list of all active sessions."""
    # This is weird, _session method allowed with only access token,
    # And also seems to expose private session information.
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
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> JSONResponse:
    """Requests 2FA OTP to be send (if configured, or skip if not required)."""

    # Check credentials.
    user = user_repo.get_user_by_login(login)
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

        tfa_otp = generate_tfa_otp(user, device_type=tfa_device)

        # Send OTP.
        email_messages.send_signin_tfa_otp_email(
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


@router.post(
    "/_session._signin", dependencies=[Depends(RateLimiter(times=3, seconds=5))]
)
async def method_session_signin(
    req: Request,
    user_agent: str = Header(""),
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> JSONResponse:
    """Authenticates user and gives new session token for user."""

    body_json = await req.json()
    if "login" not in body_json or "password" not in body_json:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`login` and `password` fields are required!",
        )
    login, password, tfa_otp = (
        body_json.get("login"),
        body_json.get("password"),
        body_json.get("tfa_otp", None),
    )

    user = user_repo.get_user_by_login(login)
    if not user and "@" in login:
        # Used for email where domain like `ya.ru` is same with `yandex.ru` or `yandex.com`
        user = user_repo.get_user_by_login(login=convert_email_to_standardized(login))

    validate_signin_fields(user=user, password=password)
    validate_user_tfa_otp_from_request(tfa_otp, user)
    token, session = publish_new_session_with_token(
        user=user, user_agent=user_agent, db=user_repo.db, req=req
    )
    return api_success(
        {
            **serialize_user(user),
            "session_token": token.encode(key=session.token_secret),
            "sid": session.id,
        }
    )
