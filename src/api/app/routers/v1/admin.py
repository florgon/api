"""
    Admin API router.
    Provides API methods (routes) for working with admin stuff.
"""

import time

from fastapi.responses import JSONResponse
from fastapi import Request, Depends, APIRouter

from app.services.user_query_filter import query_users_by_filter_query
from app.services.user import query_user_by_id_or_username
from app.services.api.response import api_success, api_error
from app.services.api.errors import ApiErrorCode
from app.services.admin import validate_user_allowed_to_call_admin_methods
from app.serializers.user import serialize_users, serialize_user
from app.serializers.offer import serialize_offers, serialize_offer
from app.database.dependencies import get_db, Session
from app.database import crud

router = APIRouter(include_in_schema=False)


@router.get("/_admin.getSessionsCounters")
async def method_admin_get_sessions_counters(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns sessions counters."""
    await validate_user_allowed_to_call_admin_methods(req, db)
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
    await validate_user_allowed_to_call_admin_methods(req, db)
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
    await validate_user_allowed_to_call_admin_methods(req, db)
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

    await validate_user_allowed_to_call_admin_methods(req, db)

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

    await validate_user_allowed_to_call_admin_methods(req, db)
    user = query_user_by_id_or_username(db, user_id, username)

    # Update user.
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)

    return api_success(serialize_user(user, in_list=False, include_private_fields=True))


@router.get("/_admin.unbanUser")
async def method_admin_unban_user(
    req: Request,
    user_id: int | None = None,
    username: str | None = None,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Activates user."""

    await validate_user_allowed_to_call_admin_methods(req, db)
    user = query_user_by_id_or_username(db, user_id, username)

    # Update user.
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)

    return api_success(serialize_user(user, in_list=False, include_private_fields=True))


@router.get("/_admin.getOffers")
async def method_admin_get_offers(
    req: Request,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Returns list of offers."""

    await validate_user_allowed_to_call_admin_methods(req, db)
    offers = crud.offer.get_list(db)

    return api_success(serialize_offers(offers))


@router.get("/_admin.getOffer")
async def method_admin_get_offer(
    req: Request,
    id: int,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Returns single offer."""

    await validate_user_allowed_to_call_admin_methods(req, db)
    offer = crud.offer.get_by_id(db, id=id)
    if offer is None:
        return api_error(
            ApiErrorCode.API_ITEM_NOT_FOUND,
            "Offer with specified ID is not found!",
        )

    return api_success(serialize_offer(offer))
