"""
    Oauth API auth routers.
"""

# Libraries.
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse

# Services.
from app.services.permissions import (
    normalize_scope,
    parse_permissions_from_scope,
    permissions_get_ttl,
    Permission,
)
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success

# Other.
from app.tokens.oauth_code import OAuthCode
from app.tokens.access_token import AccessToken
from app.tokens.session_token import SessionToken
from app.database.dependencies import get_db, Session
from app.services.request.session_check_client import session_check_client_by_request
from app.database import crud
from app.config import Settings, get_settings

router = APIRouter()


@router.get("/oauth.authorize")
async def method_oauth_authorize(
    client_id: int,
    state: str,
    redirect_uri: str,
    scope: str,
    response_type: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse | RedirectResponse:
    """Redirects to authorization screen."""

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )

    if response_type == "code" or response_type == "token":
        # If response type is valid (Authorization code flow or Implicit flow)

        # client_id - OAuth client unique identifier (Database ID).
        # state - Should be just passed to the client redirect uri, when OAuth flow finished.
        # scope - OAuth requested permissions, by Florgon OAuth specification,
        #         should be separated by comma (,). Listed in `Permission` enum.
        # response_type - OAuth flow (Authorization code flow or Implicit flow).
        #                 See documentation, or OAuth allow client method.
        # redirect_uri - Where user should be redirected after OAuth flow is finished.

        # Redirect to OAuth screen provider (web-interface),
        # with passing requested OAuth parameters.
        oauth_screen_request_url = (
            f"{settings.oauth_screen_provider_url}"
            f"?client_id={client_id}"
            f"&state={state}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope}"
            f"&response_type={response_type}"
        )
        return RedirectResponse(url=oauth_screen_request_url)

    # Requested response_type is not exists.
    return api_error(
        ApiErrorCode.API_INVALID_REQUEST,
        "Unknown `response_type` value! Allowed: code, token.",
    )


@router.get("/oauth.accessToken")
async def method_oauth_access_token(
    req: Request,
    client_id: int,
    client_secret: str,
    grant_type: str | None = None,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Resolves grant to access token."""

    if not grant_type or grant_type == "authorization_code":
        return _grant_type_authorization_code(
            req, client_id, client_secret, db, settings
        )

    if grant_type == "password":
        return api_error(
            ApiErrorCode.API_NOT_IMPLEMENTED,
            "Password grant_type is not implemented! (And will be not implemented soon).",
        )

    if grant_type == "client_credentials":
        return api_error(
            ApiErrorCode.API_NOT_IMPLEMENTED,
            "Client credentials grant_type is not implemented! (And will be not implemented soon).",
        )

    if grant_type == "refresh_token":
        return api_error(
            ApiErrorCode.API_NOT_IMPLEMENTED,
            "Refresh token grant_type is not implemented! (And will be not implemented soon).",
        )

        # Requested grant_type is not exists.
    return api_error(
        ApiErrorCode.API_INVALID_REQUEST,
        "Unknown `grant_type` value! "
        "Allowed: `authorization_code`, `password`, `client_credentials`, `refresh_token`.",
    )


@router.get("/_oauth._allowClient")
async def method_oauth_allow_client(
    req: Request,
    session_token: str,
    client_id: int,
    state: str,
    redirect_uri: str,
    scope: str,
    response_type: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """
    Allows access for specified client,
    by returning required information (code or access token) and formatted redirect_to URL.

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
    session_token_unsigned = SessionToken.decode_unsigned(session_token)
    session_id = session_token_unsigned.get_session_id()

    session = (
        crud.user_session.get_by_id(db, session_id=session_id) if session_id else None
    )
    if not session:
        return api_error(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Token has not linked to any session!"
        )
    session_check_client_by_request(db, session, req)

    session_token_signed = SessionToken.decode(session_token, key=session.token_secret)

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=session_token_signed.get_subject())
    if not user:
        return api_error(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "User with given token does not exists!",
        )
    if session.owner_id != user.id:
        return api_error(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Token session was linked to another user!"
        )

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification for OAuth client.
    if not oauth_client or not oauth_client.is_active:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )

    if response_type == "code":
        # Authorization code flow.
        # Gives code, that required to be decoded using OAuth resolve method at server-side using client secret value.
        # Should be used when there is server-side, which can resolve authorization code.
        # Read more about Florgon OAuth: https://dev.florgon.space/oauth

        # Encoding OAuth code.
        # Code should be resolved at server-side at redirect_uri, using resolve OAuth method.
        # Code should have very small time-to-live (TTL),
        # as it should be resolved to access token with default TTL immediately at server.
        scope = normalize_scope(scope)
        code = OAuthCode(
            settings.jwt_issuer,
            settings.oauth_code_jwt_ttl,
            user.id,
            session.id,
            scope,
            redirect_uri,
            client_id,
        ).encode(key=session.token_secret)

        # Constructing redirect URL with GET query parameters.
        redirect_to = f"{redirect_uri}?code={code}&state={state}"

        # Log statistics.
        crud.oauth_client_use.create(db, user_id=user.id, client_id=oauth_client.id)

        return api_success(
            {
                # Stores URL where to redirect, after allowing specified client,
                # Client should be redirected here, to finish OAuth flow.
                "redirect_to": redirect_to,
                "code": code,
            }
        )

    if response_type == "token":
        # Implicit authorization flow.
        # Simply, gives access token inside hash-link.
        # Should be used when there is no server-side, which can resolve authorization code.
        # Read more about Florgon OAuth: https://dev.florgon.space/oauth

        # Encoding access token.
        # Access token have infinity TTL, if there is scope permission given for no expiration date.
        access_token_permissions = parse_permissions_from_scope(scope)
        access_token_ttl = permissions_get_ttl(
            access_token_permissions, default_ttl=settings.access_token_jwt_ttl
        )

        access_token = AccessToken(
            settings.jwt_issuer,
            access_token_ttl,
            user.id,
            session.id,
            normalize_scope(scope),
        ).encode(key=session.token_secret)

        # Constructing redirect URL with hash-link parameters.
        # Email field should be passed only if OAuth client requested given scope permission.
        redirect_to_email_param = (
            f"&email={user.email}"
            if Permission.email in access_token_permissions
            else ""
        )
        redirect_to = (
            f"{redirect_uri}"
            f"#token={access_token}"
            f"&user_id={user.id}"
            f"&state={state}"
            f"&expires_in={access_token_ttl}{redirect_to_email_param}"
        )

        # Log statistics.
        crud.oauth_client_use.create(db, user_id=user.id, client_id=oauth_client.id)

        return api_success(
            {
                # Stores URL where to redirect, after allowing specified client,
                # Client should be redirected here, to finish OAuth flow.
                "redirect_to": redirect_to,
                "access_token": access_token,
            }
        )

    # Requested response_type is not exists.
    return api_error(
        ApiErrorCode.API_INVALID_REQUEST,
        "Unknown `response_type` value! Allowed: code, token.",
    )


def _grant_type_authorization_code(
    req: Request, client_id: int, client_secret: str, db: Session, settings: Settings
) -> JSONResponse:
    """OAuth authorization code grant type."""
    code = req.query_params.get("code", None)
    redirect_uri = req.query_params.get("redirect_uri", None)
    if not code:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`code` required for `authorization_code` grant type!",
        )
    if not redirect_uri:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`redirect_uri` required for `authorization_code` grant type!",
        )

    code_unsigned = OAuthCode.decode_unsigned(code)

    session_id = code_unsigned.get_session_id()
    session = (
        crud.user_session.get_by_id(db, session_id=session_id) if session_id else None
    )
    if not session:
        return api_error(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Code has not linked to any session!"
        )

    code_signed = OAuthCode.decode(code, key=session.token_secret)

    if redirect_uri != code_signed.get_redirect_uri():
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_REDIRECT_URI_MISMATCH,
            "redirect_uri should be same!",
        )

    if client_id != code_signed.get_client_id():
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_ID_MISMATCH,
            "Given code was obtained with different client!",
        )

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification for OAuth client.
    if not oauth_client or not oauth_client.is_active:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )

    if oauth_client.secret != client_secret:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_SECRET_MISMATCH,
            "Invalid client_secret! Please review secret, or generate new secret.",
        )

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=code_signed.get_subject())
    if not user:
        return api_error(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "Unable to find user that belongs to this code!",
        )
    if session.owner_id != user.id:
        return api_error(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Token session was linked to another user!"
        )

    # Access token have infinity TTL, if there is scope permission given for no expiration date.
    access_token_permissions = parse_permissions_from_scope(code_signed.get_scope())
    access_token_ttl = permissions_get_ttl(
        access_token_permissions, default_ttl=settings.access_token_jwt_ttl
    )

    access_token = AccessToken(
        settings.jwt_issuer,
        access_token_ttl,
        user.id,
        session.id,
        normalize_scope(code_signed.get_scope()),
    ).encode(key=session.token_secret)

    response_payload = {
        "access_token": access_token,
        "expires_in": access_token_ttl,
        "user_id": user.id,
    }

    if Permission.email in access_token_permissions:
        response_payload["email"] = user.email

    return api_success(response_payload)
