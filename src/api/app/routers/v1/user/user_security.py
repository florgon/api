"""
    User security API router.
    
    Provides methods for working with user security 
    (e.g changing email / password / phone, configuring 2FA)
"""

from fastapi.responses import JSONResponse
from fastapi import Depends, APIRouter
from app.services.request import AuthDataDependency, AuthData
from app.services.oauth.permissions import Permission
from app.services.limiter.depends import RateLimiter
from app.services.api import api_success
from app.serializers.user import serialize_user_security
from app.serializers.session import serialize_sessions
from app.database.repositories import UserSessionsRepository
from app.database.dependencies import get_repository

router = APIRouter(tags=["security"], prefix="/security")


@router.get("/")
async def info(
    auth_data: AuthData = Depends(
        AuthDataDependency(required_permissions={Permission.security})
    ),
) -> JSONResponse:
    """
    Fetch user security settings information (e.g 2FA is enabled).
    """
    return api_success(serialize_user_security(auth_data.user))


@router.get("/sessions", dependencies=[Depends(RateLimiter(times=3, seconds=10))])
async def list_sessions(
    repo: UserSessionsRepository = Depends(get_repository(UserSessionsRepository)),
    auth_data: AuthData = Depends(
        AuthDataDependency(required_permissions={Permission.security})
    ),
) -> JSONResponse:
    """
    Fetch all active sessions and current session ID.
    """
    return api_success(
        {"current_session_id": auth_data.session.id}
        | serialize_sessions(
            repo.get_by_owner_id(auth_data.session.owner_id), repo.db  # type: ignore
        )
    )
