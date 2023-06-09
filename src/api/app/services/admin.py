"""
    Service utils to worki with administrators.
"""
from fastapi import Request
from app.services.request.auth import query_auth_data_from_request
from app.services.permissions import Permission
from app.services.limiter.depends import RateLimiter
from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.database.models.user import User
from app.database.dependencies import Session
from app.config import get_settings


async def validate_user_allowed_to_call_admin_methods(
    req: Request, db: Session, user: User | None = None
) -> None:
    """
    Raises an exception if the user is not an administrator
    or project configured with disabled administrator methods.
    """
    settings = get_settings()

    if settings.admin_methods_disabled:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN, "Administration methods is disabled!"
        )

    user = (
        user
        or query_auth_data_from_request(
            req, db, required_permissions={Permission.admin}
        ).user
    )

    if not user.is_admin:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN, "You are not an administrator. Access denied."
        )
    await RateLimiter(times=2, seconds=15).check(req)


__all__ = ["validate_user_allowed_to_call_admin_methods"]
