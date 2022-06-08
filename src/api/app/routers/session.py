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

from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success
from app.services.limiter.depends import RateLimiter

from app.tokens.session_token import SessionToken
from app.serializers.user import serialize_user
from app.database.dependencies import get_db, Session
from app.database import crud
from app.config import get_settings, Settings


router = APIRouter()


@router.get("/_session._getUserInfo")
async def method_session_get_user_info(req: Request, db: Session = Depends(get_db)) -> JSONResponse:
    """ Returns user account information. """
    auth_data = query_auth_data_from_request(req, db, only_session_token=True)
    return api_success({
        **serialize_user(auth_data.user),
        "siat": auth_data.token.get_issued_at(),
        "sexp": auth_data.token.get_expires_at()
    })


@router.get("/_session._signup")
async def method_session_signup(
    req: Request,
    username: str, email: str, password: str, 
    db: Session = Depends(get_db), settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """ API endpoint to signup and create new user. """

    # Validate request for fields.
    is_valid, validation_error = validate_signup_fields(db, username, email, password)
    if not is_valid:
        return validation_error

    await RateLimiter(times=2, hours=24).check(req)
    user = crud.user.create(db=db, email=email, username=username, password=password)

    session = crud.user_session.create(db, user.id)
    token = SessionToken(settings.jwt_issuer, settings.session_token_jwt_ttl, user.id, session.id)
    return api_success({
        **serialize_user(user),
        "session_token": token.encode(key=session.token_secret),
        "sid": session.id
    })


@router.get("/_session._logout")
async def method_session_logout(req: Request, \
    revoke_all: bool = False,
    db: Session = Depends(get_db)) -> JSONResponse:
    """ Logout user over all session. """
    auth_data = query_auth_data_from_request(req, db, only_session_token=True)
    session = auth_data.session
    await RateLimiter(times=1, seconds=15).check(req)
    
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
async def method_session_signin(
    req: Request,
    login: str, password: str, 
    db: Session = Depends(get_db), settings: Settings = Depends(get_settings)
) -> JSONResponse:
    """ Authenticates user and gives new session token for user. """
  
    # Check credentials.
    user = crud.user.get_by_login(db=db, login=login)
    if not user or not check_password(password=password, hashed_password=user.password):
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid credentials for authentication (password or login).")
    await RateLimiter(times=1, seconds=15).check(req)
    
    session = crud.user_session.create(db, user.id)
    token = SessionToken(settings.jwt_issuer, settings.session_token_jwt_ttl, user.id, session.id)
    return api_success({
        **serialize_user(user),
        "session_token":  token.encode(key=session.token_secret),
        "sid": session.id
    })
