"""
    Oauth API auth routers.
"""

from app.database import crud
from app.database.dependencies import get_db

# Other.
from app.serializers.oauth_client import serialize_oauth_client, serialize_oauth_clients
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success
from app.services.limiter.depends import RateLimiter
from app.services.permissions import Permission

# Services.
from app.services.request import query_auth_data_from_request
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

# Libraries.
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/oauthClient.new")
async def method_oauth_client_new(
    display_name: str, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Creates new OAuth client"""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.oauth_clients]
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
        req, db, required_permissions=[Permission.oauth_clients]
    )
    oauth_clients = crud.oauth_client.get_by_owner_id(db=db, owner_id=auth_data.user.id)
    return api_success(
        serialize_oauth_clients(oauth_clients, include_deactivated=False)
    )


@router.get("/oauthClient.get")
async def method_oauth_client_get(
    client_id: int, db: Session = Depends(get_db)
) -> JSONResponse:
    """OAUTH API endpoint for getting oauth authorization client data."""
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )

    return api_success(serialize_oauth_client(oauth_client, display_secret=False))


@router.get("/oauthClient.expireSecret")
async def method_oauth_client_expire_secret(
    client_id: int, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """OAUTH API endpoint for expiring client secret."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.oauth_clients]
    )

    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )
    if oauth_client.owner_id != auth_data.user.id:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_FORBIDDEN,
            "You are not owner of this OAuth client!",
        )

    crud.oauth_client.expire(db=db, client=oauth_client)
    return api_success(serialize_oauth_client(oauth_client, display_secret=True))


@router.get("/oauthClient.edit")
async def method_oauth_client_update(
    client_id: int, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """OAUTH API endpoint for updating client information."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.oauth_clients]
    )
    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )
    if oauth_client.owner_id != auth_data.user.id:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_FORBIDDEN,
            "You are not owner of this OAuth client!",
        )

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
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.oauth_clients]
    )
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )
    if oauth_client.owner_id != auth_data.user.id:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_FORBIDDEN,
            "You are not owner of this OAuth client!",
        )

    return api_success(
        {
            **serialize_oauth_client(oauth_client, display_secret=False),
            "uses": crud.oauth_client_use.get_uses(db, client_id=client_id),
            "unique_users": crud.oauth_client_use.get_unique_users(
                db, client_id=client_id
            ),
        }
    )
