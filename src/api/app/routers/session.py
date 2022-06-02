"""
    Authentication session API router.
    Provides API methods (routes) for working with session (Signin, signup).
    For external authorization (obtaining `access_token`, not `session_token`) see OAuth.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.services.request import query_auth_data_from_request, Request
from app.services.validators.user import validate_signup_fields
from app.services.passwords import check_password
from app.services.tokens import encode_session_jwt_token
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success
from app.services.limiter.depends import RateLimiter

from app.serializers.user import serialize_user
from app.database.dependencies import get_db, Session
from app.database import crud
from app.config import get_settings, Settings


router = APIRouter()


@router.get("/_session._getUserInfo")
async def method_session_get_user_info(req: Request, db: Session = Depends(get_db)) -> JSONResponse:
    """ Returns user account information. """
    auth_data = query_auth_data_from_request(req, db, only_session_token=True)
    session_issued_at = auth_data.token_payload["iat"]
    session_expires_at = auth_data.token_payload["exp"]
    return api_success({
        **serialize_user(auth_data.user),
        "siat": session_issued_at,
        "sexp": session_expires_at
    })


@router.get("/_session._signup", dependencies=[Depends(RateLimiter(times=5, hours=24))])
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
        "session_token": session_token,
        "sid": session.id
    })


@router.get("/_session._logout")
async def method_session_logout(req: Request, \
    revoke_all: bool = False,
    db: Session = Depends(get_db)) -> JSONResponse:
    """ Logout user over all session. """
    auth_data = query_auth_data_from_request(req, db, only_session_token=True)
    session = auth_data.session

    if revoke_all:
        sessions = crud.user_session.get_by_owner_id(db, session.owner_id)
        for _session in sessions:
            _session.is_active = False
        db.commit()
        return api_success({
            "sids": [_session.id for _session in sessions]
        })
    
    session.is_active = False
    db.commit()
    return api_success({
        "sid": session.id
    })


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
        "session_token": session_token,
        "sid": session.id
    })
