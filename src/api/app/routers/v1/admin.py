"""
    Admin API router.
    Provides API methods (routes) for working with admin stuff.
    
    Counters simply, returns information like count in the database, when last is created and etc.

    TODO: Refactor counters with serializers / models.
"""

from fastapi.responses import JSONResponse
from fastapi import Depends, APIRouter
from app.services.user_query_filter import query_users_by_filter_query
from app.services.user import query_user_by_id_or_username
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success, api_error
from app.services.api.errors import ApiErrorCode
from app.services.admin import validate_user_allowed_to_call_admin_methods
from app.serializers.user import serialize_users, serialize_user
from app.serializers.session import serialize_session
from app.serializers.offer import serialize_offers, serialize_offer
from app.serializers.oauth_client import serialize_oauth_client
from app.database.repositories.users import UsersRepository
from app.database.dependencies import get_db, Session
from app.database import crud

router = APIRouter(
    include_in_schema=False,
    tags=["admin"],
    prefix="/admin",
    default_response_class=JSONResponse,
    dependencies=[
        Depends(validate_user_allowed_to_call_admin_methods),
        Depends(RateLimiter(times=3, seconds=3)),
    ],
)


@router.get("/session/counters")
async def session_counters(db: Session = Depends(get_db)) -> JSONResponse:
    """Get information about sessions counters in the database"""
    return api_success(
        {
            "sessions": {
                "last": serialize_session(
                    crud.user_session.get_last(db), db, in_list=True
                ),
                "all": crud.user_session.get_count(db),
                "inactive": {
                    "count": crud.user_session.get_inactive_count(db),
                    "unique": crud.user_session.get_inactive_count_grouped(db),
                },
                "active": {
                    "count": crud.user_session.get_active_count(db),
                    "unique": crud.user_session.get_active_count_grouped(db),
                },
            }
        }
    )


@router.get("/oauth/counters")
async def oauth_counters(
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Get information about oauth (for now, clients) counters in the database"""
    return api_success(
        {
            "oauth_clients": {
                "last": serialize_oauth_client(
                    crud.oauth_client.get_last(db), display_secret=False, in_list=True
                ),
                "all": crud.oauth_client.get_count(db),
                "inactive": crud.oauth_client.get_inactive_count(db),
                "active": crud.oauth_client.get_active_count(db),
            }
        }
    )


@router.get("/user/counters")
async def user_counters(
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Get information about users counters in the database"""
    count_all = crud.user.get_count(db)
    count_active = crud.user.get_active_count(db)
    return api_success(
        {
            "users": {
                "last": serialize_user(
                    crud.user.get_last(db),
                    in_list=True,
                    include_email=True,
                    include_optional_fields=True,
                    include_private_fields=True,
                    include_profile_fields=False,
                ),
                "all": count_all,
                "inactive": count_all - count_active,
                "active": count_active,
                "vip": crud.user.get_vip_count(db),
                "admin": crud.user.get_admin_count(db),
                "verified": crud.user.get_verified_count(db),
            }
        }
    )


@router.get("/user/list")
async def list_users(
    include_email: bool = False,
    include_optional_fields: bool = False,
    include_private_fields: bool = False,
    include_profile_fields: bool = False,
    filter_query: str = "",
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Get list of users, within filter query.
    """

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


@router.get("/user/ban")
async def ban_user(
    user_id: int | None = None,
    username: str | None = None,
    reason: str | None = None,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Bans user (deactivates it).
    """
    user = query_user_by_id_or_username(db, user_id, username)

    if not user.is_active or user.is_admin:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "User is already banned or unable to ban administrator!",
        )

    repo = UsersRepository(db=db)
    repo.deactivate(user, reason=reason)
    repo.finish(user)

    return api_success(
        serialize_user(
            user,
            in_list=False,
            include_private_fields=True,
            include_optional_fields=True,
        )
    )


@router.get("/user/unban")
async def unban_user(
    user_id: int | None = None,
    username: str | None = None,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Unbans user (activetes it).
    """
    user = query_user_by_id_or_username(db, user_id, username)
    if not user.is_active or user.is_admin:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "User is already banned or unable to ban administrator!",
        )

    repo = UsersRepository(db=db)
    repo.activate(user)
    repo.finish(user)

    return api_success(
        serialize_user(
            user,
            in_list=False,
            include_private_fields=True,
            include_optional_fields=True,
        )
    )


@router.get("/offer/list")
async def list_offers(
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Get list of all offers with information.
    ?TODO: Allow filtering.
    """
    return api_success(serialize_offers(crud.offer.get_all(db)))


@router.get("/offer/get")
async def get_offers(
    offer_id: int,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Get offer information for a given offer ID"""
    offer = crud.offer.get_by_id(db, id=offer_id)
    if offer is None:
        return api_error(
            ApiErrorCode.API_ITEM_NOT_FOUND,
            "Offer not found!",
        )

    return api_success(serialize_offer(offer))
