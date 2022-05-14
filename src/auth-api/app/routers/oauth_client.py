"""
    Oauth API auth routers.
"""

# Libraries.
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

# Services.
from app.services.request import try_query_user_from_request
from app.services import serializers
from app.services.api.errors import ApiErrorCode
from app.services.api.response import (
    api_error,
    api_success
)

# Other.
from app.database.dependencies import get_db
from app.database import crud
from app.config import (
    Settings, get_settings
)


router = APIRouter()


@router.get("/oauthClient.new")
async def method_oauth_client_new(display_name: str, req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Creates new OAuth client """
    is_authenticated, user_or_error, _ = try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    oauth_client = crud.oauth_client.create(db=db, owner_id=user.id, display_name=display_name)
    return api_success({
        **serializers.oauth_client.serialize(oauth_client, display_secret=True),
    })


@router.get("/oauthClient.list")
async def method_oauth_client_list(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Returns list of user owned OAuth clients. """
    is_authenticated, user_or_error, _ = try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    oauth_clients = crud.oauth_client.get_by_owner_id(db=db, owner_id=user.id)
    return api_success({
        "oauth_clients": [
            serializers.oauth_client.serialize(oauth_client, display_secret=False, in_list=True) for oauth_client in oauth_clients if oauth_client.is_active
        ],
    })

    
@router.get("/oauthClient.get")
async def method_oauth_client_get(client_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    """ OAUTH API endpoint for getting oauth authorization client data. """
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found or deactivated!")

    return api_success({
        **serializers.oauth_client.serialize(oauth_client, display_secret=False),
    })


@router.get("/oauthClient.expireSecret")
async def method_oauth_client_expire_secret(client_id: int, req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for expring client secret. """
    is_authenticated, user_or_error, _ = try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found or deactivated!")
    if oauth_client.owner_id != user.id:
        return api_error(ApiErrorCode.OAUTH_CLIENT_FORBIDDEN, "You are not owner of this OAuth client!")
    
    crud.oauth_client.expire(db=db, client=oauth_client)
    return api_success({
        **serializers.oauth_client.serialize(oauth_client, display_secret=True),
    })


@router.get("/oauthClient.edit")
async def method_oauth_client_update(client_id: int, req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for updating client information. """
    is_authenticated, user_or_error, _ = try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found or deactivated!")
    if oauth_client.owner_id != user.id:
        return api_error(ApiErrorCode.OAUTH_CLIENT_FORBIDDEN, "You are not owner of this OAuth client!")
    
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

    return api_success({
        **serializers.oauth_client.serialize(oauth_client, display_secret=False),
        "updated": is_updated
    })
