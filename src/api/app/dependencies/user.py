from fastapi import Request, Depends
from app.services.request.auth import try_query_auth_data_from_request
from app.services.api import ApiErrorException, ApiErrorCode
from app.database.repositories.users import UsersRepository, User
from app.database.dependencies import get_repository


async def get_profile_with_access(
    req: Request,
    username: str,
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> User:
    user = user_repo.get_user_by_username(username)
    if not user:
        raise ApiErrorException(
            ApiErrorCode.USER_NOT_FOUND,
            "User with requested username was not found!",
        )

    is_owner = False
    is_admin = False
    is_authenticated = False
    if not user.privacy_profile_public or not user.is_active:
        # If not public, or deactivated (check for admin).
        if auth_data := try_query_auth_data_from_request(
            req, user_repo.db, allow_external_clients=True
        ):
            is_owner = auth_data.user.id == user.id  # type: ignore
            is_admin = auth_data.user.is_admin  # type: ignore
        is_authenticated = auth_data is not None

    if not user.is_active and not is_admin:
        raise ApiErrorException(
            ApiErrorCode.USER_DEACTIVATED,
            "User profile is deactivated, please reach support if it is your profile!",
        )

    # Privacy.
    if not user.privacy_profile_public and (not is_owner and not is_admin):
        raise ApiErrorException(
            ApiErrorCode.USER_PROFILE_PRIVATE,
            "Requested user preferred to keep his profile private!",
        )

    if user.privacy_profile_require_auth and not is_authenticated:
        raise ApiErrorException(
            ApiErrorCode.USER_PROFILE_AUTH_REQUIRED,
            "Requested user preferred to show his profile only for authorized users!",
        )

    return user
