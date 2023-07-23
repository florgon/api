"""
    Authentication session API router.
    Provides API methods (routes) for working with session (Signin, signup).
    For external authorization (obtaining `access_token`, not `session_token`) see OAuth.
"""

from fastapi.responses import JSONResponse
from fastapi import Request, Header, Depends, Body, BackgroundTasks, APIRouter
from app.services.validators.user import (
    validate_signup_fields,
    validate_signin_fields,
    convert_email_to_standardized,
)
from app.services.tfa import validate_user_tfa_otp_from_request, generate_tfa_otp
from app.services.session import publish_new_session_with_token
from app.services.request.signup_host_allowance import validate_signup_host_allowance
from app.services.request.direct_auth import check_direct_auth_is_allowed
from app.services.request import AuthDataDependency, AuthData
from app.services.permissions import Permission
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success, api_error
from app.services.api.errors import ApiErrorCode
from app.serializers.user import serialize_user
from app.serializers.session import serialize_sessions
from app.email import messages as email_messages
from app.database.repositories import UsersRepository
from app.database.dependencies import get_repository, get_db, Session
from app.database import crud
from app.config import get_settings, Settings

router = APIRouter(
    include_in_schema=False,
    tags=["session"],
    prefix="/session",
    default_response_class=JSONResponse,
    dependencies=[],
)


@router.get("/info")
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
    "/signup",
    dependencies=[
        Depends(RateLimiter(times=3, hours=12)),
        Depends(check_direct_auth_is_allowed),
    ],
)
async def signup(
    req: Request,
    user_agent: str = Header(""),
    settings: Settings = Depends(get_settings),
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    payload: dict = Body(),
) -> JSONResponse:
    """API endpoint to signup and create new user."""
    if not settings.signup_open_registration:
        return api_error(
            ApiErrorCode.API_FORBIDDEN,
            "User signup closed (Registration forbidden by server administrator)",
        )

    if "username" not in payload or "email" not in payload or "password" not in payload:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`username`, `email` and `password` fields are required!",
        )

    username = payload.get("username", "")
    email = payload.get("email", "")
    password = payload.get("password", "")
    phone_number = payload.get("phone_number", "")

    # Used for email where domain like `ya.ru` is same with `yandex.ru` or `yandex.com`
    email = convert_email_to_standardized(email)  # type: ignore

    validate_signup_host_allowance(db=user_repo.db, request=req)
    validate_signup_fields(user_repo.db, username, email, password, phone_number)
    if not (user := user_repo.create(username, email, password, phone_number)):
        return api_error(
            ApiErrorCode.API_TRY_AGAIN_LATER,
            "Unable to create account at this time, please try again later.",
        )
    token, session = publish_new_session_with_token(
        user=user, user_agent=user_agent, db=user_repo.db, req=req
    )
    return api_success(
        {
            **serialize_user(user),
            "session_token": token.encode(key=session.token_secret),  # type: ignore
            "sid": session.id,
        }
    )


@router.get(
    "/logout",
    dependencies=[
        Depends(RateLimiter(times=1, minutes=1)),
        Depends(check_direct_auth_is_allowed),
    ],
)
async def logout(
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
            db, owner_id=auth_data.user.id  # type: ignore
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


@router.get("/list", dependencies=[Depends(RateLimiter(times=3, seconds=10))])
async def list_sessions(
    db: Session = Depends(get_db),
    auth_data: AuthData = Depends(
        AuthDataDependency(
            only_session_token=False, required_permissions={Permission.sessions}
        )
    ),
) -> JSONResponse:
    """Returns list of all active sessions."""
    # This is weird, _session method allowed with only access token,
    # And also seems to expose private session information.
    current_session = auth_data.session
    sessions = crud.user_session.get_active_by_owner_id(db, current_session.owner_id)  # type: ignore
    return api_success(
        {
            **serialize_sessions(sessions, db=db),
            "current_id": current_session.id,
        }
    )


@router.get(
    "/tfa/otp/request",
    dependencies=[
        Depends(RateLimiter(times=1, minutes=1)),
        Depends(check_direct_auth_is_allowed),
    ],
)
async def request_tfa_otp(
    login: str,
    password: str,
    background_tasks: BackgroundTasks,
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> JSONResponse:
    """Requests 2FA OTP to be send (if configured, or skip if not required)."""

    user = validate_signin_fields(
        user=user_repo.get_user_by_login(login), password=password
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

        tfa_otp: str = generate_tfa_otp(user, device_type=tfa_device)  # type: ignore

        # Send OTP.
        email_messages.send_signin_tfa_otp_email(
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


@router.post(
    "/signin",
    dependencies=[
        Depends(RateLimiter(times=3, seconds=5)),
        Depends(check_direct_auth_is_allowed),
    ],
)
async def signin(
    req: Request,
    user_agent: str = Header(""),
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    payload: dict = Body(),
) -> JSONResponse:
    """Authenticates user and gives new session token for user."""

    if "login" not in payload or "password" not in payload:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`login` and `password` fields are required!",
        )

    login = payload.get("login", "")
    tfa_otp = payload.get("tfa_otp", "")
    password = payload.get("password", "")

    user = user_repo.get_user_by_login(login)
    if not user and "@" in login:
        # Used for email where domain like `ya.ru` is same with `yandex.ru` or `yandex.com`
        user = user_repo.get_user_by_login(login=convert_email_to_standardized(login))

    user = validate_signin_fields(user=user, password=password)

    validate_user_tfa_otp_from_request(tfa_otp, user)
    token, session = publish_new_session_with_token(
        user=user, user_agent=user_agent, db=user_repo.db, req=req
    )
    return api_success(
        {
            **serialize_user(user),
            "session_token": token.encode(key=session.token_secret),  # type: ignore
            "sid": session.id,
        }
    )
