"""
    Oauth API auth routers.
"""

# Libraries.
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, RedirectResponse

# Services.
from app.services.tokens import encode_access_jwt_token
from app.services.api.errors import ApiErrorCode
from app.services.api.response import (
    api_error,
    api_success
)

# Other.
from app.services.tokens import (
    try_decode_session_jwt_token, encode_access_jwt_token
)
from app.services.oauth_code import (
    encode_oauth_jwt_code, try_decode_oauth_jwt_code
)
from app.services.permissions import normalize_scope
from app.database.dependencies import get_db, Session
from app.database import crud
from app.config import (
    Settings, get_settings
)


router = APIRouter()


@router.get("/oauth.authorize")
async def method_oauth_authorize(client_id: int, state: str, redirect_uri: str, scope: str, response_type: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Redirects to authorization screen. """
    
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found or deactivated!")

    if response_type == "code" or response_type == "token":
        return RedirectResponse(url=f"{settings.oauth_screen_provider_url}?client_id={client_id}&state={state}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}")
    return api_error(ApiErrorCode.API_INVALID_REQUEST, "Unknown `response_type` field! Should be one of those: `code`, `token`")


@router.get("/oauth.accessToken")
async def method_oauth_access_token(code: str, client_id: int, client_secret: str, redirect_uri: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Resolves given code. """
    is_valid, code_payload_or_error, _ = try_decode_oauth_jwt_code(code, settings.jwt_secret)
    if not is_valid:
        return code_payload_or_error
    code_payload = code_payload_or_error
    code_scope = code_payload["scope"]

    if redirect_uri != code_payload["redirect_uri"]:
        return api_error(ApiErrorCode.OAUTH_CLIENT_REDIRECT_URI_MISMATCH, "redirect_uri should be same!")

    if client_id != code_payload["client_id"]:
        return api_error(ApiErrorCode.OAUTH_CLIENT_ID_MISMATCH, "Given code was obtained with different client!")

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification for OAuth client.
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found or deactivated!")

    if oauth_client.secret != client_secret:
        return api_error(ApiErrorCode.OAUTH_CLIENT_SECRET_MISMATCH, "Invalid client_secret!")

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=code_payload["sub"])
    if not user:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Unable to find user that belongs to this code!")

    access_token = encode_access_jwt_token(user, normalize_scope(code_scope), settings.jwt_issuer, settings.access_token_jwt_ttl, settings.jwt_secret)
    return api_success({
        "access_token": access_token,
        "expires_in": settings.access_token_jwt_ttl,
        "user_id": user.id
    })


@router.get("/_oauth._allowClient")
async def method_oauth_allow_client(session_token: str, client_id: int, state: str, redirect_uri: str, scope: str, response_type: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    """ Allows access for specified client, by returning required information and formatted redirect_to URL. """
    # Validate session token.
    is_valid, token_payload_or_error, _ = try_decode_session_jwt_token(session_token, settings.jwt_secret)
    if not is_valid:
        return token_payload_or_error
    session_token_payload = token_payload_or_error

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=session_token_payload["sub"])
    if not user:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "User with given token does not exists!")

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification for OAuth client.
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found or deactivated!")

    if response_type == "code" or response_type == "token":
        if response_type == "code":
            # Authorization code flow.
            # Gives code, that requires to be decoded using method.
            code = encode_oauth_jwt_code(user, client_id, redirect_uri, scope, settings.jwt_issuer, settings.oauth_code_jwt_ttl, settings.jwt_secret)
            return api_success({
                "redirect_to": f"{redirect_uri}?code={code}&state={state}",
                "code": code
            })
        if response_type == "token":
            # Implicit authorization flow.
            # Simply, gives access token inside hash-link.
            access_token = encode_access_jwt_token(user, normalize_scope(scope), settings.jwt_issuer, settings.access_token_jwt_ttl, settings.jwt_secret)
            return api_success({
                "redirect_to": f"{redirect_uri}#token={access_token}&user_id={user.id}&state={state}&expires_in={settings.access_token_jwt_ttl}",
                "access_token": access_token
            })

    # Invalid response type.
    return api_error(ApiErrorCode.API_INVALID_REQUEST, "Unknown `response_type` field! Should be `code` or `token`.")