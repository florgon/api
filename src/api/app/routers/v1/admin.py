"""
    Admin API router.
    Provides API methods (routes) for working with admin stuff.
"""

import time

from app.config import get_settings
from app.database import crud
from app.database.dependencies import Session, get_db
from app.database.models.user import User
from app.serializers.user import serialize_user, serialize_users
from app.services.api.errors import ApiErrorCode, ApiErrorException
from app.services.api.response import api_error, api_success
from app.services.limiter.depends import RateLimiter
from app.services.permissions import Permission
from app.services.request import query_auth_data_from_request
from app.services.user_query_filter import query_users_by_filter_query
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

router = APIRouter(include_in_schema=False)


async def validate_admin_method_allowed(req: Request, db: Session) -> None:
    """
    Validates that the method is allowed to be called.
    """
    if get_settings().admin_methods_disabled:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN, "Admin methods are disabled by administrator!"
        )

    auth_data = query_auth_data_from_request(
        req, db, required_permissions={Permission.admin}
    )
    if not auth_data.user.is_admin:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN, "You are not an administrator. Access denied."
        )
    await RateLimiter(times=2, seconds=15).check(req)


def query_user_by_id_or_username(
    db: Session, user_id: int | None = None, username: str | None = None
) -> User:
    """Returns user by id or username or raises an exception if failed to query."""
    if user_id is None and username is None:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST, "user_id or username required!"
        )
    if user_id is not None and username is not None:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST, "Please pass only user_id or username!"
        )

    user = (
        crud.user.get_by_id(db, user_id)
        if username is None
        else crud.user.get_by_username(db, username)
    )
    if not user:
        raise ApiErrorException(ApiErrorCode.USER_NOT_FOUND, "User not found!")

    return user


@router.get("/_admin.getSessionsCounters")
async def method_admin_get_sessions_counters(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns sessions counters."""
    await validate_admin_method_allowed(req, db)
    return api_success(
        {
            "sessions": {
                "time_last_created": time.mktime(
                    crud.user_session.get_last(db).time_created.timetuple()
                ),
                "all": crud.user_session.get_count(db),
                "inactive": {
                    "count": crud.user_session.get_inactive_count(db),
                    "grouped": crud.user_session.get_inactive_count_grouped(db),
                },
                "active": {
                    "count": crud.user_session.get_active_count(db),
                    "grouped": crud.user_session.get_active_count_grouped(db),
                },
            }
        }
    )


@router.get("/_admin.getOauthClientsCounters")
async def method_admin_get_oauth_clients_counters(
    req: Request,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Returns OAuth clients counters."""
    await validate_admin_method_allowed(req, db)
    return api_success(
        {
            "oauth_clients": {
                "time_last_created": time.mktime(
                    crud.oauth_client.get_last(db).time_created.timetuple()
                ),
                "all": crud.oauth_client.get_count(db),
                "inactive": crud.oauth_client.get_inactive_count(db),
                "active": crud.oauth_client.get_active_count(db),
            }
        }
    )


@router.get("/_admin.getUsersCounters")
async def method_admin_get_users_counters(
    req: Request,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Returns users counters."""
    await validate_admin_method_allowed(req, db)
    return api_success(
        {
            "users": {
                "time_last_created": time.mktime(
                    crud.user.get_last(db).time_created.timetuple()
                ),
                "all": crud.user.get_count(db),
                "inactive": crud.user.get_inactive_count(db),
                "active": crud.user.get_active_count(db),
                "vip": crud.user.get_vip_count(db),
                "admin": crud.user.get_admin_count(db),
                "verified": crud.user.get_verified_count(db),
            }
        }
    )


@router.get("/_admin.listUsers")
async def method_admin_list_users(
    req: Request,
    include_email: bool = False,
    include_optional_fields: bool = False,
    include_private_fields: bool = False,
    include_profile_fields: bool = False,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Creates new mailing task (Permitted only)."""

    await validate_admin_method_allowed(req, db)

    filter_query = req.query_params.get(
        "filter",
    )
    if not filter_query:
        return api_error(ApiErrorCode.API_INVALID_REQUEST, "Filter string required!")

    users = query_users_by_filter_query(db, filter_query)

    return api_success(
        {"total_count": len(users)}
        | serialize_users(
            users,
            include_email=include_email,
            include_optional_fields=include_optional_fields,
            include_private_fields=include_private_fields,
            include_profile_fields=include_profile_fields,
        )
    )


@router.get("/_admin.banUser")
async def method_admin_ban_user(
    req: Request,
    user_id: int | None = None,
    username: str | None = None,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Deactivates user."""

    await validate_admin_method_allowed(req, db)
    user = query_user_by_id_or_username(db, user_id, username)

    # Update user.
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)

    return api_success(serialize_user(user, in_list=False, include_private_fields=True))


@router.get("/_admin.unbanUser")
async def method_admin_unban_usre(
    req: Request,
    user_id: int | None = None,
    username: str | None = None,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Activates user."""

    await validate_admin_method_allowed(req, db)
    user = query_user_by_id_or_username(db, user_id, username)

    # Update user.
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)

    return api_success(serialize_user(user, in_list=False, include_private_fields=True))
