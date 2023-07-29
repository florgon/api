"""
    User profile API router.
    
    Provides methods to work with user profiles (e.g. public users)
"""

from fastapi.responses import JSONResponse
from fastapi import Depends, APIRouter
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success
from app.serializers.user import serialize_user
from app.dependencies.user import get_profile_with_access, User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", dependencies=[Depends(RateLimiter(times=3, seconds=1))])
async def get_user_profile(
    profile: User = Depends(get_profile_with_access),
) -> JSONResponse:
    """
    Returns public information about the user (his profile) by username,
    if their privacy settings allows access for you.
    """
    return api_success(
        serialize_user(
            profile,
            include_optional_fields=True,
            include_profile_fields=True,
        )
    )
