"""
    Oauth API auth routers.
"""

# Libraries.
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse

# Services.
from app import services
from app.services import serializers
from app.services.api.errors import ApiErrorCode
from app.services.api.response import (
    api_error,
    api_success
)

# Other.
from app import database
from app.database import crud
from app.config import (
    Settings, get_settings
)

# Database dependency.
get_db = database.dependencies.get_db

# Fast API router.
router = APIRouter()


@router.get("/oauth/direct")
async def oauth_direct(client_id: int, client_secret: str, login: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for direct oauth authorization (Should be dissalowed by external clients). """

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification for OAuth client.
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "OAuth client not found or deactivated!")
    if oauth_client.secret != client_secret:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid OAuth client secret.")
    
    # Query user.
    user = crud.user.get_by_login(db=db, login=login)

    # Check credentials.
    if not user or not services.passwords.check_password(password=password, hashed_password=user.password):
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid credentials")

    # Generate token.
    token = services.jwt.encode(user, settings.jwt_issuer, settings.jwt_ttl, settings.jwt_secret)

    # Return user with token.
    return api_success({
        **serializers.user.serialize(user),
        "token": token
    })


@router.get("/oauth/authorize")
async def oauth_external(client_id: int, state: str, redirect_uri: str, scope: str, response_type: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for external OAuth authorization (Not implemented yet). """

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification for OAuth client.
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found or deactivated!")

    if response_type == "code" or response_type == "token":
        # Redirect to auth provider.
        if response_type == "code":
            return api_error(ApiErrorCode.API_INVALID_REQUEST, "OAuth code authorization flow is not implemented yet!")
        return RedirectResponse(url=f"{settings.oauth_screen_provider_url}?client_id={client_id}&state={state}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}")

    # Invalid response type.
    return api_error(ApiErrorCode.API_INVALID_REQUEST, "Unknown `response_type` field! Should be one of those: `code`, `token`")


@router.get("/oauth/token")
async def oauth_resolve_code(code: str, db: Session = Depends(get_db)) -> JSONResponse:
    """ OAUTH API endpoint for external OAuth authorization (Not implemented yet). """

    # Not implemented
    return api_error(ApiErrorCode.API_NOT_IMPLEMENTED, "External OAuth with code flow is not implemented yet!")


@router.get("/oauth/client/new")
async def oauth_client_new(display_name: str, req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for creating new oauth authorization client. """

    # Try authenticate.
    is_authenticated, user_or_error, _ = services.request.try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    # Create new client.
    oauth_client = crud.oauth_client.create(db=db, owner_id=user.id, display_name=display_name)

    # Return client.
    return api_success({
        **serializers.oauth_client.serialize(oauth_client, display_secret=True),
    })


@router.get("/oauth/client/list")
async def oauth_client_list(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint that returns list of user owned OAuth clients. """

    # Try authenticate.
    is_authenticated, user_or_error, _ = services.request.try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    # Query OAuth clients.
    oauth_clients = crud.oauth_client.get_by_owner_id(db=db, owner_id=user.id)

    # Return user with token.
    return api_success({
        "oauth_clients": [
            serializers.oauth_client.serialize(oauth_client, display_secret=False, in_list=True) for oauth_client in oauth_clients
        ],
    })

    
@router.get("/oauth/client/get")
async def oauth_client_get(client_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    """ OAUTH API endpoint for getting oauth authorization client data. """

    # Query client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification.
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found or deactivated!")
        
    # Return client.
    return api_success({
        **serializers.oauth_client.serialize(oauth_client, display_secret=False),
    })


@router.get("/oauth/client/expire")
async def oauth_client_expire(client_id: int, req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for expring client secret. """

    # Try authenticate.
    is_authenticated, user_or_error, _ = services.request.try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification.
    if not oauth_client:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found!")
    if oauth_client.owner_id != user.id:
        return api_error(ApiErrorCode.OAUTH_CLIENT_FORBIDDEN, "You are not owner of this OAuth client!")
    
    # Generate new OAuth token.
    crud.oauth_client.expire(db=db, client=oauth_client)

    # Return user with token.
    return api_success({
        **serializers.oauth_client.serialize(oauth_client, display_secret=True),
    })


@router.get("/oauth/client/update")
async def oauth_client_update(client_id: int, req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for updating client information. """

    # Try authenticate.
    is_authenticated, user_or_error, _ = services.request.try_query_user_from_request(req, db, settings.jwt_secret)
    if not is_authenticated:
        return user_or_error
    user = user_or_error

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification.
    if not oauth_client:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found!")
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

    # Return user with token.
    return api_success({
        **serializers.oauth_client.serialize(oauth_client, display_secret=False),
        "updated": is_updated
    })
