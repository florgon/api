"""
    User API router.
    
    Provides user get / set info methods, get another user information.
"""

from fastapi.responses import JSONResponse
from fastapi import Depends, APIRouter
from app.services.request import AuthDataDependency, AuthData
from app.services.permissions import Permission
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success
from app.serializers.user import serialize_user
from app.schemas.user import UpdateModel
from app.dependencies.user import get_profile_with_access, User
from app.database.repositories.users import UsersRepository
from app.database.dependencies import get_repository

router = APIRouter(
    include_in_schema=True,
    tags=["user"],
    prefix="/user",
    default_response_class=JSONResponse,
)


@router.get("/")
async def info(
    auth_data: AuthData = Depends(AuthDataDependency()),
) -> JSONResponse:
    """
    Fetch all information about current user with access token.

    Email and phone will be only returned if there is email or phone permission for token.
    """
    # TODO: Return back cache or rate limiter.
    has_access_to_email = Permission.email in auth_data.permissions
    has_access_to_phone = Permission.phone in auth_data.permissions
    return api_success(
        serialize_user(
            user=auth_data.user,
            include_optional_fields=True,
            include_private_fields=True,
            include_profile_fields=True,
            include_email=has_access_to_email,
            include_phone=has_access_to_phone,
        )
    )


@router.get("/profile", dependencies=[Depends(RateLimiter(times=3, seconds=1))])
async def profile(
    profile: User = Depends(get_profile_with_access),
) -> JSONResponse:
    """
    Returns public information about the user (their profile) by username
    if their privacy settings allows access for you.
    """
    # TODO: Return back cache.
    return api_success(
        serialize_user(
            profile,
            include_optional_fields=True,
            include_profile_fields=True,
        )
    )


@router.post("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update(
    model: UpdateModel,
    auth_data: AuthData = Depends(
        AuthDataDependency(required_permissions={Permission.edit})
    ),
    repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> JSONResponse:
    """
    Updates current user information, requires edit permission.

    Field names can be found at the documentation.
    """

    is_updated = repo.apply_update_model(model, auth_data.user)

    return api_success(
        serialize_user(
            auth_data.user,
            include_profile_fields=True,
            include_private_fields=True,
        )
        | {"is_updated": is_updated}
    )
