"""
    User account API router.
    Provides API methods (routes) for working with user account.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.services.permissions import Permission
from app.services.request import query_auth_data_from_request
from app.services.api.response import api_success, api_error
from app.services.api.errors import ApiErrorCode, ApiErrorException
from app.services.limiter.depends import RateLimiter
from app.serializers.user import serialize_user
from app.database import crud

from app.database.dependencies import get_db, Session

router = APIRouter()


@router.get("/user.getInfo")
async def method_user_get_info(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns user account information."""
    auth_data = query_auth_data_from_request(req, db)
    email_allowed = Permission.email in auth_data.permissions
    return api_success(
        serialize_user(
            auth_data.user,
            **{
                "include_email": email_allowed,
                "include_optional_fields": True,
                "include_private_fields": True,
                "include_profile_fields": True,
            },
        )
    )


@router.get(
    "/user.getProfileInfo", dependencies=[Depends(RateLimiter(times=3, seconds=1))]
)
async def method_user_get_profile_info(
    req: Request,
    user_id: int | None = None,
    username: str | None = None,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Returns user account profile information."""
    user = None

    if user_id is None and username is None:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST, "user_id or username required!"
        )
    if user_id is not None and username is not None:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST, "Please pass only user_id or username!"
        )

    if user_id is not None:
        user = crud.user.get_by_id(db, user_id)
    elif username is not None:
        user = crud.user.get_by_username(db, username)

    # User.
    if not user:
        return api_error(
            ApiErrorCode.USER_NOT_FOUND,
            f"User with requested {'username' if user_id is None else 'id'} was not found!",
        )
    if not user.is_active:
        return api_error(
            ApiErrorCode.USER_DEACTIVATED,
            "Unable to get user, due to user account deactivation!",
        )

    # Privacy.
    if not user.privacy_profile_public:
        try:
            auth_data = query_auth_data_from_request(
                req, db, allow_external_clients=True
            )
            if auth_data.user.id != user.id:
                raise ApiErrorException
        except ApiErrorException:
            return api_error(
                ApiErrorCode.USER_PROFILE_PRIVATE,
                "Requested user preferred to keep his profile private!",
            )

    if user.privacy_profile_require_auth:
        try:
            query_auth_data_from_request(req, db, allow_external_clients=True)
        except ApiErrorException:
            return api_error(
                ApiErrorCode.USER_PROFILE_AUTH_REQUIRED,
                "Requested user preferred to show his profile only for authorized users!",
            )

    return api_success(
        serialize_user(
            user,
            **{
                "include_email": False,
                "include_optional_fields": True,
                "include_private_fields": False,
                "include_profile_fields": True,
            },
        )
    )


@router.get("/user.getCounters")
async def method_user_get_counter(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns user account counters (Count of different items, like for badges)."""
    auth_data = query_auth_data_from_request(req, db)
    return api_success(
        {
            "oauth_clients": crud.oauth_client.get_count_by_owner_id(
                db, auth_data.user.id
            )
        }
    )


@router.get("/user.setInfo")
async def method_user_set_info(
    req: Request,
    first_name: str | None = None,
    last_name: str | None = None,
    sex: bool | None = None,
    avatar_url: str | None = None,
    privacy_profile_public: bool | None = None,
    privacy_profile_require_auth: bool | None = None,
    profile_bio: str | None = None,
    profile_website: str | None = None,
    profile_social_username_gh: str | None = None,
    profile_social_username_vk: str | None = None,
    profile_social_username_tg: str | None = None,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Updates user account information."""

    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.edit]
    )
    user = auth_data.user

    # Notice:
    # IK this is trash,
    # but this is temporary solution,
    # and will be rewritten later.
    is_updated = False
    if first_name is not None and first_name != user.first_name:
        user.first_name = first_name
        is_updated = True
    if last_name is not None and last_name != user.last_name:
        user.last_name = last_name
        is_updated = True
    if sex is not None and sex != user.sex:
        user.sex = sex
        is_updated = True
    if avatar_url is not None and avatar_url != user.avatar:
        user.avatar = avatar_url
        is_updated = True
    if (
        privacy_profile_public is not None
        and privacy_profile_public != user.privacy_profile_public
    ):
        user.privacy_profile_public = privacy_profile_public
        is_updated = True
    if (
        privacy_profile_require_auth is not None
        and privacy_profile_require_auth != user.privacy_profile_require_auth
    ):
        user.privacy_profile_require_auth = privacy_profile_require_auth
        is_updated = True
    if profile_bio is not None and profile_bio != user.profile_bio:
        user.profile_bio = profile_bio
        is_updated = True
    if profile_website is not None and profile_website != user.profile_website:
        user.profile_website = profile_website
        is_updated = True
    if (
        profile_social_username_gh is not None
        and profile_social_username_gh != user.profile_social_username_gh
    ):
        user.profile_social_username_gh = profile_social_username_gh
        is_updated = True
    if (
        profile_social_username_vk is not None
        and profile_social_username_vk != user.profile_social_username_vk
    ):
        user.profile_social_username_vk = profile_social_username_vk
        is_updated = True
    if (
        profile_social_username_tg is not None
        and profile_social_username_tg != user.profile_social_username_tg
    ):
        user.profile_social_username_tg = profile_social_username_tg
        is_updated = True

    if is_updated:
        db.commit()

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
