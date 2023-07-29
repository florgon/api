"""
    User API router.
    
    Provides method get or patch your (user) information methods.
"""

from fastapi.responses import JSONResponse
from fastapi import Depends, APIRouter
from app.services.request import AuthDataDependency, AuthData
from app.services.permissions import Permission
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success
from app.serializers.user import serialize_user
from app.schemas.user import UpdateModel
from app.database.repositories import UsersRepository
from app.database.dependencies import get_repository

router = APIRouter()


@router.get("/")
async def get_user_info(
    auth_data: AuthData = Depends(AuthDataDependency()),
) -> JSONResponse:
    """
    Fetch all information about current user with access token.

    Email and phone will be only returned if there is email or phone permission for token.
    """
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


@router.patch("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def patch_user_info(
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

    return api_success(
        {"is_updated": repo.apply_update_model(model, auth_data.user)}
        | serialize_user(
            auth_data.user,
            include_profile_fields=True,
            include_private_fields=True,
        )
    )
