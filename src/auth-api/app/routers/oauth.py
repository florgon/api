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
from app.services.permissions import normalize_scope, parse_permissions_from_scope, Permission
from app.database.dependencies import get_db, Session
from app.database import crud
from app.config import (
    Settings, get_settings
)


router = APIRouter()


@router.get("/oauth.authorize")
async def method_oauth_authorize(client_id: int, state: str, redirect_uri: str, scope: str, response_type: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Redirects to authorization screen. """
    
    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(ApiErrorCode.OAUTH_CLIENT_NOT_FOUND, "OAuth client not found or deactivated!")

    if response_type == "code" or response_type == "token":
        # If response type is valid (Authorization code flow or Implicit flow)

        # client_id - OAuth client unique identifier (Database ID).
        # state - Should be just passed to the client redirect uri, when OAuth flow finished.
        # scope - OAuth requested permissions, by Florgon OAuth specification, should be separated by comma (,). Listed in `Permission` enum.
        # response_type - OAuth flow (Authorization code flow or Implicit flow). See documentation, or OAuth allow client method.
        # redirect_uri - Where user should be redirected after OAuth flow is finished.

        # Redirect to OAuth screen provider (web-interface),
        # with passing requested OAuth parameters.
        oauth_screen_request_url = f"{settings.oauth_screen_provider_url}?client_id={client_id}&state={state}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}"
        return RedirectResponse(url=oauth_screen_request_url)
    
    # Requested response_type is not exists.
    return api_error(ApiErrorCode.API_INVALID_REQUEST, "Unknown `response_type` value! Allowed: code, token.")


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

    access_token_permissions = parse_permissions_from_scope(code_scope)
    access_token_ttl = 0 if Permission.noexpire in access_token_permissions else settings.access_token_jwt_ttl 
    access_token = encode_access_jwt_token(user, normalize_scope(code_scope), settings.jwt_issuer, access_token_ttl, settings.jwt_secret)

    response_payload = {
        "access_token": access_token,
        "expires_in": access_token_ttl,
        "user_id": user.id,
    }

    if Permission.email in access_token_permissions:
        response_payload["email"] = user.email

    return api_success(response_payload)


@router.get("/_oauth._allowClient")
async def method_oauth_allow_client(session_token: str, \
    client_id: int, state: str, redirect_uri: str, scope: str, response_type: str, \
    db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ 
        Allows access for specified client, by returning required information (code or access token) and formatted redirect_to URL. 

        :param session_token: Session token, that obtained by authorizing user on Florgon, should be used ONLY by Florgon.
        :param client_id: OAuth client unique identifier (Database ID).
        :param state: Should be just passed to the client redirect uri, when OAuth flow finished.
        :param redirect_uri: Where user should be redirected after OAuth flow is finished.
        :param scope: OAuth requested permissions, by Florgon OAuth specification, should be separated by comma (,). Listed in `Permission` enum.
        :param response_type: OAuth flow (Authorization code flow or Implicit flow). See documentation, or OAuth allow client method.

        :param db: Database session dependency.
        :param settings: Config settings dependency.

        :returns: API response.
    """

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

    if response_type == "code":
        # Authorization code flow.
        # Gives code, that required to be decoded using OAuth resolve method at server-side using client secret value.
        # Should be used when there is server-side, which can resolve authorization code.
        # Read more about Florgon OAuth: https://dev.florgon.space/oauth

        # Encoding OAuth code.
        # Code should be resolved at server-side at redirect_uri, using resolve OAuth method.
        # Code should have very small time-to-live (TTL), as it should be resolved to access token with default TTL immediatly at server.
        code = encode_oauth_jwt_code(user, client_id, redirect_uri, scope, settings.jwt_issuer, settings.oauth_code_jwt_ttl, settings.jwt_secret)
        
        # Constructing redirect URL with GET query parameters.
        redirect_to = f"{redirect_uri}?code={code}&state={state}"

        return api_success({
            # Stores URL where to redirect, after allowing specified client,
            # Client should be redirected here, to finish OAuth flow.
            "redirect_to": redirect_to,
            "code": code
        })
    
    if response_type == "token":
        # Implicit authorization flow.
        # Simply, gives access token inside hash-link.
        # Should be used when there is no server-side, which can resolve authorization code.
        # Read more about Florgon OAuth: https://dev.florgon.space/oauth
        
        # Encoding access token.
        # Access token have infinity TTL, if there is scope permission given for no expiration date.
        access_token_permissions = parse_permissions_from_scope(scope)
        access_token_ttl = 0 if Permission.noexpire in access_token_permissions else settings.access_token_jwt_ttl 
        access_token = encode_access_jwt_token(user, normalize_scope(scope), settings.jwt_issuer, access_token_ttl, settings.jwt_secret)

        # Constructing redirect URL with hash-link parameters.
        # Email field should be passed only if OAuth client requested given scope permission.
        redirect_to_email_param = f"&email={user.email}" if Permission.email in access_token_permissions else ""
        redirect_to = f"{redirect_uri}#token={access_token}&user_id={user.id}&state={state}&expires_in={access_token_ttl}{redirect_to_email_param}"

        return api_success({
            # Stores URL where to redirect, after allowing specified client,
            # Client should be redirected here, to finish OAuth flow.
            "redirect_to": redirect_to,
            "access_token": access_token
        })

    # Requested response_type is not exists.
    return api_error(ApiErrorCode.API_INVALID_REQUEST, "Unknown `response_type` value! Allowed: code, token.")