"""
    Authentication session API router.
    Provides API methods (routes) for working with session (Signin, signup).
    For external authorization (obtaining `access_token`, not `session_token`) see OAuth.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.services.request import try_query_user_from_request, Request
from app.services.validators.user import validate_signup_fields
from app.services.passwords import check_password
from app.services.tokens import encode_session_jwt_token
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success
from app.services.serializers.user import serialize_user

from app.database.dependencies import get_db, Session
from app.database import crud
from app.config import get_settings, Settings


router = APIRouter()


@router.get("/_session._getUserInfo")
async def method_session_get_user_info(req: Request, db: Session = Depends(get_db)) -> JSONResponse:
    """ Returns user account information. """

    # Authentication, query user.
    is_authenticated, user_or_error, token_payload = try_query_user_from_request(req, db, allow_session_token=True)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    if not user.is_active:
        return api_error(ApiErrorCode.USER_DEACTIVATED, "Cannot get user information, due to user account deactivation!")

    session_issued_at = token_payload["iat"]
    session_expires_at = token_payload["exp"]
    return api_success({
        **serialize_user(user_or_error),
        "siat": session_issued_at,
        "sexp": session_expires_at
    })


@router.get("/_session._signup")
async def method_session_signup(username: str, email: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ API endpoint to signup and create new user. """

    # Validate request for fields.
    is_valid, validation_error = validate_signup_fields(db, username, email, password)
    if not is_valid:
        return validation_error

    user = crud.user.create(db=db, email=email, username=username, password=password)

    session = crud.user_session.create(db, user.id)
    session_token = encode_session_jwt_token(user, session, settings.jwt_issuer, settings.session_token_jwt_ttl)
    return api_success({
        **serialize_user(user),
        "session_token": session_token
    })


@router.get("/_session._logout")
async def method_session_logout(req: Request, db: Session = Depends(get_db)) -> JSONResponse:
    """ Logout user over all session. """

    # Authentication, query user.
    is_authenticated, user_or_error, _ = try_query_user_from_request(req, db, allow_session_token=True)
    if not is_authenticated:
        return user_or_error
    _ = user_or_error

    return api_error(ApiErrorCode.API_NOT_IMPLEMENTED, "Logout from all devices is not implemented yet")


@router.get("/_session._signin")
async def method_session_signin(login: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Authenticates user and gives new session token for user. """

    # Check credentials.
    user = crud.user.get_by_login(db=db, login=login)
    if not user or not check_password(password=password, hashed_password=user.password):
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid credentials for authentication (password or login).")

    session = crud.user_session.create(db, user.id)
    session_token = encode_session_jwt_token(user, session, settings.jwt_issuer, settings.session_token_jwt_ttl)
    return api_success({
        **serialize_user(user),
        "session_token": session_token
    })
