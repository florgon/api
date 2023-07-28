"""
    Session API methods.
    
    Session - is a base authentication container for later working with access tokens.
    All access tokens is linked to the session, which is authentication process container.
    
    Provides base signin (login) and signup (register) process alongside with logout.
    
    IF you are interested in external usage of the API, please look at the Florgon OAuth and access token (external services workflow).
    
    Notice: 
    All session methods can only be used by Florgon (internal web page or etc),
    so, even if you are want to use that methods, you will be rejected and get forbidden error.
"""

from fastapi.responses import JSONResponse
from fastapi import Request, Depends, APIRouter
from app.services.session import publish_new_session_with_token
from app.services.request.direct_auth import check_direct_auth_is_allowed
from app.services.request import AuthDataDependency, AuthData
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success, api_error
from app.services.api.errors import ApiErrorCode
from app.serializers.user import serialize_user
from app.schemas.session import LogoutModel, AuthModel
from app.dependencies.session import get_valid_signup_user, get_valid_signin_user, User
from app.database.repositories import UserSessionsRepository
from app.database.dependencies import get_repository, get_db, Session

router = APIRouter(
    include_in_schema=False,
    tags=["session"],
    prefix="/session",
    default_response_class=JSONResponse,
    dependencies=[Depends(check_direct_auth_is_allowed)],
)


@router.get("/info", dependencies=[Depends(RateLimiter(times=2, seconds=1))])
async def info(
    auth_data: AuthData = Depends(AuthDataDependency(only_session_token=True)),
) -> JSONResponse:
    """
    Fetch information about session token alongside with user associated to the session.

    Should be only used for checking out that session token is valid one or get basic information about user (for re-authentication after).
    ?TODO: Checkout / migrate on the check session token method?
    """
    return api_success(
        {
            **serialize_user(auth_data.user),
            "issued_at": auth_data.token.get_issued_at(),
            "expires_at": auth_data.token.get_expires_at(),
        }
    )


@router.get("/logout", dependencies=[Depends(RateLimiter(times=1, minutes=1))])
async def logout(
    model: LogoutModel,
    repo: UserSessionsRepository = Depends(get_repository(UserSessionsRepository)),
    auth_data: AuthData = Depends(AuthDataDependency(only_session_token=True)),
) -> JSONResponse:
    """
    Close sessions (logout).

    Logout from all sessions (or all except current).
    Logout current session (or specified by ID).
    """

    sessions = [auth_data.session]
    if model.revoke_all:
        sessions = repo.get_by_owner_id(owner_id=auth_data.user.id)  # type: ignore
        if model.exclude_current:
            sessions = filter(lambda session: session.is_active, sessions)
    elif model.session_id and (session := repo.get_by_id(model.session_id)):
        sessions = [session]

    if not sessions:
        return api_error(ApiErrorCode.API_ITEM_NOT_FOUND, "No sessions to close!")

    repo.deactivate_list(sessions)
    return api_success({})


@router.post("/signup", dependencies=[Depends(RateLimiter(times=3, hours=12))])
async def signup(
    req: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_valid_signup_user),
) -> JSONResponse:
    """
    Sign-up (register) to get session token.
    Returns token and session ID.
    """
    token, session_id = publish_new_session_with_token(user=user, db=db, req=req)
    return api_success(AuthModel(session_token=token, sid=session_id))


@router.post("/signin", dependencies=[Depends(RateLimiter(times=3, seconds=5))])
async def signin(
    req: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_valid_signin_user),
) -> JSONResponse:
    """
    Sign-in (login) to get session token.
    Requires 2FA authentication if user is configured it.
    Returns token and session ID (Session can be old one, according to implementation of the authorization process).
    """
    token, session_id = publish_new_session_with_token(user=user, db=db, req=req)
    return api_success(AuthModel(session_token=token, sid=session_id))
