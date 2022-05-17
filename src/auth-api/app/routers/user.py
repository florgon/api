"""
    User account API router.
    Provides API methods (routes) for working with user account.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.services.permissions import parse_permissions_from_scope, Permission
from app.services.request import try_query_user_from_request
from app.services.api.response import api_success, api_error
from app.services.api.errors import ApiErrorCode
from app.services.serializers.user import serialize_user
from app.database import crud

from app.database.dependencies import get_db, Session
from app.config import get_settings, Settings


router = APIRouter()


# TODO: Updating user account information.
# TODO: User password recovery.
# TODO: [User account deletion request]
# TODO: [2FA]


@router.get("/user.getInfo")
async def method_user_get_info(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Returns user account information. """

    # Authentication, query user.
    is_authenticated, user_or_error, token_payload = try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error
    permissions = parse_permissions_from_scope(token_payload["scope"])

    if not user.is_active:
        return api_error(ApiErrorCode.USER_DEACTIVATED, "Cannot get user information, due to user account deactivation!")

    return api_success(serialize_user(user_or_error, include_email=True, include_optional_fields=True))


@router.get("/user.getCounters")
async def method_user_get_counter(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Returns user account counters (Count of different items, like for badges). """

    # Authentication, query user.
    is_authenticated, user_or_error, _ = try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    if not user.is_active:
        return api_error(ApiErrorCode.USER_DEACTIVATED, "Cannot get user information, due to user account deactivation!")

    return api_success({
        "oauth_clients": crud.oauth_client.get_count_by_owner_id()
    })


@router.get("/user.setInfo")
async def method_user_set_info(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Updates user account information. """

    # Authentication, query user.
    is_authenticated, user_or_error, _ = try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    if not user.is_active:
        return api_error(ApiErrorCode.USER_DEACTIVATED, "Cannot update user information, due to user account deactivation!")

    return api_error(ApiErrorCode.API_NOT_IMPLEMENTED, "Updating user account information is not implemented yet!")