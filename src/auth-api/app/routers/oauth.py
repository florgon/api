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


@router.get("/oauth")
async def oauth_root() -> JSONResponse:
    """ OAuth root page. """
    return api_success({
        "methods": [
            "/oauth/direct",
            "/oauth/authorize",
            "/oauth/token",
            "/oauth/client/",
        ]
    })


@router.get("/oauth/client")
async def oauth_client_root() -> JSONResponse:
    """ OAuth root page. """
    return api_success({
        "methods": [
            "/oauth/client/new",
            "/oauth/client/expire",
            "/oauth/client/get"
        ]
    })


@router.get("/oauth/direct")
async def oauth_direct(client_id: int, client_secret: str, login: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for direct oauth authorization (Should be dissalowed by external clients). """

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification for OAuth client.
    if not oauth_client:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "OAuth client not found!")
    if oauth_client.secret != client_secret:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid OAuth client secret.")
    if not oauth_client.is_verified:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Given OAuth client is not verified, and forbidden to use direct OAUTH!")

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
async def oauth_external(client_id: int, state: str, redirect_uri: str, scope: str, response_type: str, db: Session = Depends(get_db)) -> JSONResponse:
    """ OAUTH API endpoint for external OAuth authorization (Not implemented yet). """

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification for OAuth client.
    if not oauth_client:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found!")

    if response_type == "code" or response_type == "token":
        # Redirect to auth provider.
        if response_type == "code":
            return api_error(ApiErrorCode.API_INVALID_REQUEST, "OAuth code authorization flow is not implemented yet!")
        return RedirectResponse(url=f"https://auth.florgon.space?client_id={client_id}&state={state}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}")

    # Invalid response type.
    return api_error(ApiErrorCode.API_INVALID_REQUEST, "Unknown `response_type` field! Should be one of those: `code`, `token`")


@router.get("/oauth/token")
async def oauth_resolve_code(code: str, db: Session = Depends(get_db)) -> JSONResponse:
    """ OAUTH API endpoint for external OAuth authorization (Not implemented yet). """

    # Not implemented
    return api_error(ApiErrorCode.API_NOT_IMPLEMENTED, "External OAuth with code flow is not implemented yet!")


@router.get("/oauth/client/new")
async def oauth_client_new(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for creating new oauth authorization client. """

    # Try authenticate.
    is_authenticated, token_payload_or_error, _ = services.request.try_decode_token_from_request(req, settings.jwt_secret)
    if not is_authenticated:
        return token_payload_or_error
    token_payload = token_payload_or_error
    
    # Query user.
    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])

    # Create new client.
    oauth_client = crud.oauth_client.create(db=db, owner_id=user.id)

    # Return client.
    return api_success({
        **serializers.oauth_client.serialize(oauth_client),
    })


@router.get("/oauth/client/get")
async def oauth_client_get(client_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    """ OAUTH API endpoint for getting oauth authorization client data. """

    # Query client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id.id)

    # Verification.
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found or deactivated!")
        
    # Return client.
    return api_success({
        **serializers.oauth_client.serialize(oauth_client, display_secret=False),
    })


@router.get("/oauth/client/expire")
async def oauth_client_expire(client_id: int, req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for direct oauth authorization (Should be dissalowed by external clients). """

    # Try authenticate.
    is_authenticated, token_payload_or_error, _ = services.request.try_decode_token_from_request(req, settings.jwt_secret)
    if not is_authenticated:
        return token_payload_or_error
    token_payload = token_payload_or_error
    
    # Query user.
    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])

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
