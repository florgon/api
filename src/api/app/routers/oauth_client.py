"""
    Oauth API auth routers.
"""

import time

from app.database import crud
from app.database.dependencies import get_db
from app.database.models.oauth_client import OAuthClient
from app.serializers.oauth_client import serialize_oauth_client, serialize_oauth_clients
from app.services.api.errors import ApiErrorCode, ApiErrorException
from app.services.api.response import api_error, api_success
from app.services.cache import JSONResponseCoder, plain_cache_key_builder
from app.services.limiter.depends import RateLimiter
from app.services.permissions import Permission, parse_permissions_from_scope
from app.services.request import query_auth_data_from_request
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

router = APIRouter(tags=["oauthClient"])


def _query_oauth_client_with_owner(
    db: Session, client_id: int, owner_id: int
) -> OAuthClient:
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        raise ApiErrorException(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )
    if oauth_client.owner_id != owner_id:
        raise ApiErrorException(
            ApiErrorCode.OAUTH_CLIENT_FORBIDDEN,
            "You are not owner of this OAuth client!",
        )
    return oauth_client


@router.get("/oauthClient.new")
async def method_oauth_client_new(
    display_name: str, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Creates new OAuth client"""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions={Permission.oauth_clients}
    )
    if not auth_data.user.is_verified:
        return api_error(
            ApiErrorCode.USER_EMAIL_NOT_CONFIRMED,
            "Please confirm your email, before accessing OAuth clients!",
        )
    await RateLimiter(times=2, minutes=30).check(req)

    oauth_client = crud.oauth_client.create(
        db=db, owner_id=auth_data.user.id, display_name=display_name
    )
    return api_success(serialize_oauth_client(oauth_client, display_secret=True))


@router.get("/oauthClient.list")
async def method_oauth_client_list(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns list of user owned OAuth clients."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions={Permission.oauth_clients}
    )
    oauth_clients = crud.oauth_client.get_by_owner_id(db=db, owner_id=auth_data.user.id)
    return api_success(
        serialize_oauth_clients(oauth_clients, include_deactivated=False)
    )


@router.get("/oauthClient.getLinked")
async def method_oauth_client_get_linked(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """OAUTH API endpoint for getting linked oauth clients."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions={Permission.oauth_clients}
    )
    oauth_client_users = crud.oauth_client_user.get_by_user_id(
        db, user_id=auth_data.user.id
    )

    return api_success(
        {
            "linked_oauth_clients": [
                {
                    **serialize_oauth_client(
                        client_user.oauth_client, display_secret=False
                    ),
                    **{
                        "requested_scope": client_user.requested_scope,
                        "requested_at": time.mktime(
                            client_user.time_created.timetuple()
                        ),
                        "request_updated_at": time.mktime(
                            client_user.time_updated.timetuple()
                        )
                        if client_user.time_updated
                        else None,
                    },
                }
                for client_user in oauth_client_users
            ]
        }
    )


@router.get("/oauthClient.unlink")
async def method_oauth_client_unlink(
    client_id: int, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """OAUTH API endpoint for unlinking linked oauth clients."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions={Permission.oauth_clients}
    )
    oauth_client_user = crud.oauth_client_user.get_by_client_and_user_id(
        db, user_id=auth_data.user.id, client_id=client_id
    )
    if not oauth_client_user or not oauth_client_user.is_active:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not linked!",
        )

    oauth_client_user.is_active = False
    db.add(oauth_client_user)
    db.commit()

    return api_success({"unlinked_client_id": oauth_client_user.client_id})


@router.get("/oauthClient.get")
@cache(
    expire=60,
    coder=JSONResponseCoder,
    key_builder=plain_cache_key_builder,
    namespace="routers_oauth_clients_getter",
)
async def method_oauth_client_get(
    req: Request,
    client_id: int,
    check_is_linked: bool = False,
    scope: str = "",
    db: Session = Depends(get_db),
) -> JSONResponse:
    """OAUTH API endpoint for getting oauth authorization client data."""
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )

    response = serialize_oauth_client(oauth_client, display_secret=False)
    if check_is_linked:
        auth_data = query_auth_data_from_request(
            req=req, db=db, only_session_token=True
        )
        oauth_client_user = crud.oauth_client_user.get_by_client_and_user_id(
            db, client_id=client_id, user_id=auth_data.user.id
        )
        response |= {
            "is_linked": oauth_client_user is not None
            and parse_permissions_from_scope(oauth_client_user.requested_scope)
            == parse_permissions_from_scope(scope),
        }

    return api_success(response)


@router.get("/oauthClient.expireSecret")
async def method_oauth_client_expire_secret(
    client_id: int, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """OAUTH API endpoint for expiring client secret."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions={Permission.oauth_clients}
    )

    oauth_client = _query_oauth_client_with_owner(db, client_id, auth_data.user.id)
    crud.oauth_client.expire(db=db, client=oauth_client)

    return api_success(serialize_oauth_client(oauth_client, display_secret=True))


@router.get("/oauthClient.edit")
async def method_oauth_client_update(
    client_id: int, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """OAUTH API endpoint for updating client information."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions={Permission.oauth_clients}
    )
    # Query OAuth client.
    oauth_client = _query_oauth_client_with_owner(db, client_id, auth_data.user.id)

    # Updating.
    is_updated = False
    display_name = req.query_params.get("display_name")
    display_avatar_url = req.query_params.get("display_avatar_url")
    if display_name and display_name != oauth_client.display_name:
        oauth_client.display_name = display_name
        is_updated = True
    if display_avatar_url and display_avatar_url != oauth_client.display_avatar:
        oauth_client.display_avatar = display_avatar_url
        is_updated = True

    if is_updated:
        db.commit()
        await FastAPICache.clear("routers_oauth_clients_getter")

    return api_success(
        {
            **serialize_oauth_client(oauth_client, display_secret=False),
            "updated": is_updated,
        }
    )


@router.get("/oauthClient.stats")
async def method_oauth_client_stats(
    client_id: int, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """OAUTH API endpoint for getting oauth authorization client usage data."""
    user_id = query_auth_data_from_request(
        req, db, required_permissions={Permission.oauth_clients}
    ).user.id
    oauth_client = _query_oauth_client_with_owner(db, client_id, user_id)

    return api_success(
        {
            **serialize_oauth_client(oauth_client, display_secret=False),
            "uses": crud.oauth_client_use.get_uses(db, client_id=client_id),
            "unique_users": crud.oauth_client_use.get_unique_users(
                db, client_id=client_id
            ),
        }
    )
