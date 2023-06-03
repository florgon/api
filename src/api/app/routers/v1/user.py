"""
    User account API router.
    Provides API methods (routes) for working with user account.
"""

import pydantic
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi.responses import JSONResponse
from fastapi import Request, Depends, APIRouter
from app.services.validators.user import (
    validate_username_field,
    validate_profile_website_field,
    validate_profile_social_username_field,
    validate_profile_bio_field,
    validate_phone_number_field,
    validate_last_name_field,
    validate_first_name_field,
    validate_email_field,
    convert_email_to_standardized,
)
from app.services.request import (
    try_query_auth_data_from_request,
    AuthDataDependency,
    AuthData,
)
from app.services.permissions import Permission
from app.services.limiter.depends import RateLimiter
from app.services.cache import authenticated_cache_key_builder, JSONResponseCoder
from app.services.api.response import api_success, api_error
from app.services.api.errors import ApiErrorCode
from app.serializers.user import serialize_user
from app.database.repositories.users import UsersRepository
from app.database.dependencies import get_repository, get_db, Session
from app.database import crud
from app.config import get_settings

router = APIRouter(tags=["user"])


@router.get("/user.getInfo")
@cache(
    expire=60,
    coder=JSONResponseCoder,
    key_builder=authenticated_cache_key_builder,
    namespace="routers_user_info_getter",
)
async def method_user_get_info(
    auth_data: AuthData = Depends(AuthDataDependency()),
) -> JSONResponse:
    """Returns user account information."""
    email_allowed = Permission.email in auth_data.permissions
    return api_success(
        serialize_user(
            user=auth_data.user,
            include_email=email_allowed,
            include_optional_fields=True,
            include_private_fields=True,
            include_profile_fields=True,
        )
    )


@router.get(
    "/user.getProfileInfo", dependencies=[Depends(RateLimiter(times=3, seconds=1))]
)
async def method_user_get_profile_info(
    req: Request,
    user_id: int | None = None,
    username: str | None = None,
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> JSONResponse:
    """Returns user account profile information."""
    profile_user = None

    if user_id is None and username is None:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST, "user_id or username required!"
        )
    if user_id is not None and username is not None:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST, "Please pass only user_id or username!"
        )

    if user_id is not None:
        profile_user = user_repo.get_user_by_id(user_id)
    elif username is not None:
        profile_user = user_repo.get_user_by_username(username)

    # User.
    if not profile_user:
        return api_error(
            ApiErrorCode.USER_NOT_FOUND,
            f"User with requested {'username' if user_id is None else 'id'} was not found!",
        )

    is_owner = False
    is_admin = False
    is_authenticated = False
    if not profile_user.privacy_profile_public or not profile_user.is_active:
        # If not public, or deactivated (check for admin).
        is_authenticated, auth_data = try_query_auth_data_from_request(
            req, user_repo.db, allow_external_clients=True
        )
        if is_authenticated:
            is_owner = auth_data.user.id == profile_user.id
            is_admin = auth_data.user.is_admin

    # If banned, raise error if not admin.
    if not profile_user.is_active and not is_admin:
        return api_error(
            ApiErrorCode.USER_DEACTIVATED,
            "Unable to get user, due to user account deactivation!",
        )

    # Privacy.
    if not profile_user.privacy_profile_public and (not is_owner and not is_admin):
        return api_error(
            ApiErrorCode.USER_PROFILE_PRIVATE,
            "Requested user preferred to keep his profile private!",
        )

    if profile_user.privacy_profile_require_auth and not is_authenticated:
        return api_error(
            ApiErrorCode.USER_PROFILE_AUTH_REQUIRED,
            "Requested user preferred to show his profile only for authorized users!",
        )

    return api_success(
        serialize_user(
            profile_user,
            **{
                "include_email": False,
                "include_optional_fields": True,
                "include_private_fields": False,
                "include_profile_fields": True,
            },
        )
    )


@router.get("/user.setInfo")
async def method_user_set_info(
    req: Request,
    auth_data: AuthData = Depends(
        AuthDataDependency(required_permissions={Permission.edit})
    ),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Updates user account information."""

    user = auth_data.user

    allowed_fields = (
        "email",
        "phone_number",
        "username",
        "first_name",
        "last_name",
        "sex",
        "profile_bio",
        "profile_website",
        "profile_social_username_vk",
        "profile_social_username_tg",
        "profile_social_username_gh",
        "security_tfa_enabled",
        "privacy_profile_require_auth",
        "privacy_profile_public",
    )
    new_fields = {
        k: v
        for k, v in req.query_params.items()
        if v is not None and k in allowed_fields and getattr(user, k, None) != v
    }
    settings = get_settings()

    for name, value in new_fields.items():
        if name == "username":
            validate_username_field(db, settings, username=value)
        if name == "email":
            email = convert_email_to_standardized(value)
            validate_email_field(db, settings, email=email)
            crud.user.email_unverify(db=db, user=user)
        if name == "first_name":
            validate_first_name_field(value)
        if name == "last_name":
            validate_last_name_field(value)
        if name == "profile_bio":
            validate_profile_bio_field(value)
        if name == "profile_website":
            validate_profile_website_field(value)
        if name == "phone_number":
            validate_phone_number_field(db, value)
        if name.startswith("profile_social_username"):
            validate_profile_social_username_field(value)

        if name in (
            "sex",
            "privacy_profile_public",
            "privacy_profile_require_auth",
            "security_tfa_enabled",
            "privacy_profile_require_auth",
            "privacy_profile_public",
        ):
            setattr(user, name, pydantic.parse_obj_as(bool, value))
        else:
            setattr(user, name, value)

    is_updated = bool(new_fields)
    if is_updated:
        db.commit()
        await FastAPICache.clear("routers_user_info_getter")

    return api_success(
        {
            **serialize_user(
                user,
                include_email=False,
                include_optional_fields=False,
                include_profile_fields=True,
                include_private_fields=True,
            ),
            "updated": is_updated,
        }
    )
