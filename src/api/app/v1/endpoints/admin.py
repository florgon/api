"""
    Admin API router.
    Provides API methods (routes) for working with admin stuff.
"""

import time

from app.core.config import Settings, get_settings
from app.core.database import crud
from app.core.database.dependencies import Session, get_db
from app.core.services.api.errors import ApiErrorCode, ApiErrorException
from app.core.services.api.response import api_success
from app.core.services.limiter.depends import RateLimiter
from app.core.services.permissions import Permission
from app.core.services.request import query_auth_data_from_request
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

router = APIRouter()


async def validate_admin_method_allowed(req: Request, db: Session, settings: Settings):
    """
    Validates that the method is allowed to be called.
    """
    if settings.admin_methods_disabled:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN, "Admin methods are disabled by administrator!"
        )

    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.admin]
    )
    if not auth_data.user.is_admin:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN, "You are not an administrator. Access denied."
        )
    await RateLimiter(times=2, seconds=15).check(req)


@router.get("/admin/counters/sessions")
async def method_admin_get_sessions_counters(
    req: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Returns sessions counters."""
    validate_admin_method_allowed(req, db, settings)
    return api_success(
        {
            "sessions": {
                "time_last_created": time.mktime(
                    crud.user_session.get_last(db).time_created.timetuple
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


@router.get("/admin/counters/oauth_clients")
async def method_admin_get_oauth_clients_counters(
    req: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Returns OAuth clients counters."""
    validate_admin_method_allowed(req, db, settings)
    return api_success(
        {
            "oauth_clients": {
                "time_last_created": time.mktime(
                    crud.oauth_client.get_last(db).time_created.timetuple
                ),
                "all": crud.oauth_client.get_count(db),
                "inactive": crud.oauth_client.get_inactive_count(db),
                "active": crud.oauth_client.get_active_count(db),
            }
        }
    )


@router.get("/admin/counters/users")
async def method_admin_get_users_counters(
    req: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Returns users counters."""
    validate_admin_method_allowed(req, db, settings)
    return api_success(
        {
            "users": {
                "time_last_created": time.mktime(
                    crud.user.get_last(db).time_created.timetuple
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
