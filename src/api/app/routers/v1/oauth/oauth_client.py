"""
    Oauth API auth routers.
"""

import time

from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import Request, Depends, APIRouter
from app.services.request.auth import AuthDataDependency, AuthData
from app.services.request import query_auth_data_from_request
from app.services.oauth.permissions import scopes_is_same, Permission
from app.services.oauth import query_oauth_client
from app.services.limiter.depends import RateLimiter
from app.services.api import api_success, api_error, ApiErrorCode
from app.serializers.oauth_client import serialize_oauth_clients, serialize_oauth_client
from app.database.repositories import (
    OAuthClientUserRepository,
    OAuthClientUseRepository,
    OAuthClientsRepository,
)
from app.database.dependencies import get_repository, get_db

router = APIRouter(tags=["client"], prefix="/client")


@router.post("/", dependencies=[Depends(RateLimiter(times=2, minutes=30))])
async def create_client(
    display_name: str,
    repo: OAuthClientsRepository = Depends(get_repository(OAuthClientsRepository)),
    auth_data: AuthData = Depends(
        AuthDataDependency(
            required_permissions={Permission.oauth_clients}, allow_not_confirmed=False
        )
    ),
) -> JSONResponse:
    """Creates new OAuth client"""

    return api_success(
        serialize_oauth_client(
            repo.create(owner_id=auth_data.user.id, display_name=display_name),  # type: ignore
            display_secret=True,
        )
    )


@router.get("/list")
async def list_clients(
    repo: OAuthClientsRepository = Depends(get_repository(OAuthClientsRepository)),
    auth_data: AuthData = Depends(
        AuthDataDependency(
            required_permissions={Permission.oauth_clients}, allow_not_confirmed=False
        )
    ),
) -> JSONResponse:
    """Returns list of user owned OAuth clients."""
    return api_success(
        serialize_oauth_clients(
            repo.get_by_owner_id(auth_data.user.id), include_deactivated=False  # type: ignore
        )
    )


@router.get("/linked")
async def get_linked_clients(
    repo: OAuthClientUserRepository = Depends(
        get_repository(OAuthClientUserRepository)
    ),
    auth_data: AuthData = Depends(
        AuthDataDependency(required_permissions={Permission.oauth_clients})
    ),
) -> JSONResponse:
    """OAUTH API endpoint for getting linked oauth clients."""

    return api_success(
        {
            "linked_oauth_clients": [
                {
                    serialize_oauth_client(user.oauth_client, display_secret=False)
                    | {
                        "requested_scope": user.requested_scope,
                        "requested_at": time.mktime(user.time_created.timetuple()),
                        "request_updated_at": time.mktime(user.time_updated.timetuple())
                        if user.time_updated
                        else None,
                    },
                }
                for user in repo.get_by_user_id(auth_data.user.id)  # type: ignore
            ]
        }
    )


@router.post("/unlink")
async def unlink_client(
    client_id: int,
    repo: OAuthClientUserRepository = Depends(
        get_repository(OAuthClientUserRepository)
    ),
    auth_data: AuthData = Depends(
        AuthDataDependency(required_permissions={Permission.oauth_clients})
    ),
) -> JSONResponse:
    """OAUTH API endpoint for unlinking linked oauth clients."""
    oauth_client_user = repo.get_by_client_and_user_id(auth_data.user.id, client_id)  # type: ignore
    if not oauth_client_user or not oauth_client_user.is_active:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not linked!",
        )

    oauth_client_user.is_active = False  # type: ignore
    repo.finish(oauth_client_user)

    return api_success({"unlinked_client_id": oauth_client_user.client_id})


@router.get("/")
async def get_client(
    req: Request,
    client_id: int,
    check_is_linked: bool = False,
    scope: str = "",
    db: Session = Depends(get_db),
    repo: OAuthClientsRepository = Depends(get_repository(OAuthClientsRepository)),
    auth_data: AuthData = Depends(AuthDataDependency()),
) -> JSONResponse:
    """OAUTH API endpoint for getting oauth authorization client data."""
    oauth_client = repo.get_by_id(client_id, is_active=True)
    if not oauth_client:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )

    response = serialize_oauth_client(oauth_client, display_secret=False)
    if check_is_linked:
        auth_data = query_auth_data_from_request(
            req=req, db=db, only_session_token=True
        )
        oauth_client_user = OAuthClientUserRepository(
            repo.db
        ).get_by_client_and_user_id(
            auth_data.user.id, client_id  # type: ignore
        )  # type: ignore
        response |= {
            "is_linked": oauth_client_user is not None
            and scopes_is_same(scope, oauth_client_user.requested_scope)
        }

    return api_success(response)


@router.post("/secret/refresh")
async def method_oauth_client_expire_secret(
    client_id: int,
    repo: OAuthClientsRepository = Depends(get_repository(OAuthClientsRepository)),
    auth_data: AuthData = Depends(
        AuthDataDependency(
            required_permissions={Permission.oauth_clients}, allow_not_confirmed=False
        )
    ),
) -> JSONResponse:
    """OAUTH API endpoint for expiring client secret."""

    oauth_client = query_oauth_client(repo.db, client_id, auth_data.user.id)  # type: ignore
    repo.expire(client=oauth_client)

    return api_success(serialize_oauth_client(oauth_client, display_secret=True))


@router.get("/patch", deprecated=True)
async def method_oauth_client_update(
    client_id: int, req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """OAUTH API endpoint for updating client information."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions={Permission.oauth_clients}
    )
    # Query OAuth client.
    oauth_client = query_oauth_client(db, client_id, auth_data.user.id)

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


@router.get("/stats")
async def method_oauth_client_stats(
    client_id: int,
    repo: OAuthClientUseRepository = Depends(get_repository(OAuthClientUseRepository)),
    auth_data: AuthData = Depends(
        AuthDataDependency(required_permissions={Permission.oauth_clients})
    ),
) -> JSONResponse:
    """Fetch usage statistics of your OAuth client, like total uses, unique users."""
    oauth_client = query_oauth_client(repo.db, client_id, auth_data.user.id)  # type: ignore

    return api_success(
        {
            **serialize_oauth_client(oauth_client, display_secret=False),
            "uses": repo.get_uses(client_id),
            "unique_users": repo.get_unique_users(client_id),
        }
    )
