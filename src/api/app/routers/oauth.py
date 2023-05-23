"""
    Oauth API auth routers.
"""

from urllib.parse import parse_qs

from app.config import Settings, get_settings
from app.database import crud
from app.database.dependencies import Session, get_db
from app.database.models.oauth_client import OAuthClient
from app.oauth_grants import resolve_grant
from app.services.api.errors import ApiErrorCode, ApiErrorException
from app.services.api.response import api_error, api_success
from app.services.permissions import (
    Permission,
    normalize_scope,
    parse_permissions_from_scope,
    permissions_get_ttl,
)
from app.services.request.auth import query_auth_data_from_request
from app.tokens import AccessToken, OAuthCode
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter(tags=["oauth"])


def _query_oauth_client(db: Session, client_id: int) -> OAuthClient:
    """
    Returns oauth client by id or raises API error if not found or inactive.
    """
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        raise ApiErrorException(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )
    return oauth_client


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

    _query_oauth_client(db, client_id)
    if response_type in ("code", "token"):
        oauth_screen_request_url = (
            f"{settings.auth_oauth_screen_provider_url}"
            f"?client_id={client_id}"
            f"&state={state}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope}"
            f"&response_type={response_type}"
        )
        return RedirectResponse(url=oauth_screen_request_url)
    return api_error(
        ApiErrorCode.API_INVALID_REQUEST,
        "Unknown `response_type` value! Allowed: code, token.",
    )


@router.post("/oauth.accessToken")
async def method_oauth_access_token_post(
    req: Request,
    client_id: int = 0,
    client_secret: str | None = None,
    grant_type: str | None = None,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Resolves grant to access token."""
    body_query = parse_qs((await req.body()).decode(encoding="UTF-8"))
    client_secret = body_query.get("client_secret", [client_secret])[0]
    client_id = int(body_query.get("client_id", [client_id])[0])
    grant_type = body_query.get("grant_type", [grant_type])[0]
    if not client_id or not client_secret:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`client_id` and `client_secret` is required!",
        )
    return await resolve_grant(
        grant_type=grant_type,
        req=req,
        client_id=client_id,
        client_secret=client_secret,
        db=db,
        settings=settings,
    )


@router.get("/oauth.accessToken")
async def method_oauth_access_token_get(
    req: Request,
    client_id: int,
    client_secret: str,
    grant_type: str | None = None,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Resolves grant to access token."""

    return await resolve_grant(
        grant_type=grant_type,
        req=req,
        client_id=client_id,
        client_secret=client_secret,
        db=db,
        settings=settings,
    )


@router.get("/_oauth._allowClient", include_in_schema=False)
async def method_oauth_allow_client(
    req: Request,
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

    :param client_id: OAuth client unique identifier (Database ID).
    :param state: Should be just passed to the client redirect uri, when OAuth flow finished.
    :param redirect_uri: Where user should be redirected after OAuth flow is finished.
    :param scope: OAuth requested permissions, by Florgon OAuth specification, should be separated by comma (,). Listed in `Permission` enum.
    :param response_type: OAuth flow (Authorization code flow or Implicit flow). See documentation, or OAuth allow client method.
    """

    auth_data = query_auth_data_from_request(req=req, db=db, only_session_token=True)
    oauth_client = _query_oauth_client(db=db, client_id=client_id)

    user, session = auth_data.user, auth_data.session

    response = None
    if response_type == "code":
        # Authorization code flow.
        # Gives code, that required to be decoded using OAuth resolve method at server-side using client secret value.
        # Should be used when there is server-side, which can resolve authorization code.
        # Read more about Florgon OAuth: https://florgon.com/dev/oauth

        # Encoding OAuth code.
        # Code should be resolved at server-side at redirect_uri, using resolve OAuth method.
        # Code should have very small time-to-live (TTL),
        # as it should be resolved to access token with default TTL immediately at server.
        scope = normalize_scope(scope)
        time_to_live = settings.security_oauth_code_tokens_ttl
        code = OAuthCode(
            settings.security_tokens_issuer,
            time_to_live,
            user.id,
            session.id,
            scope,
            redirect_uri,
            client_id,
            code_id=crud.oauth_code.create(
                db=db, user_id=user.id, session_id=session.id, client_id=client_id
            ).id,
        ).encode(key=session.token_secret)

        # Constructing redirect URL with GET query parameters.
        redirect_to = f"{redirect_uri}?code={code}&state={state}"

        response = {
            # Stores URL where to redirect, after allowing specified client,
            # Client should be redirected here, to finish OAuth flow.
            "redirect_to": redirect_to,
            "code": code,
        }

    if response_type == "token":
        # Implicit authorization flow.
        # Simply, gives access token inside hash-link.
        # Should be used when there is no server-side, which can resolve authorization code.
        # Read more about Florgon OAuth: https://florgon.com/dev/oauth

        # Encoding access token.
        # Access token have infinity TTL, if there is scope permission given for no expiration date.
        access_token_permissions = parse_permissions_from_scope(scope)
        access_token_ttl = permissions_get_ttl(
            access_token_permissions, default_ttl=settings.security_access_tokens_ttl
        )

        access_token = AccessToken(
            settings.security_tokens_issuer,
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

        response = {
            # Stores URL where to redirect, after allowing specified client,
            # Client should be redirected here, to finish OAuth flow.
            "redirect_to": redirect_to,
            "access_token": access_token,
        }

    if response:
        # Log statistics and save oauth user.
        crud.oauth_client_use.create(db, user_id=user.id, client_id=oauth_client.id)
        crud.oauth_client_user.create_if_not_exists(
            db, user_id=user.id, client_id=oauth_client.id, scope=normalize_scope(scope)
        )
        return api_success(response)

    # Requested response_type is not exists.
    return api_error(
        ApiErrorCode.API_INVALID_REQUEST,
        "Unknown `response_type` value! Allowed: code, token.",
    )


@router.get("/_oauth._clientIsLinked", include_in_schema=False)
async def method_oauth_client_is_linked(
    req: Request,
    client_id: int,
    scope: str,
    db: Session = Depends(get_db),
):
    """
    Returns is requested client is linked to user or not.
    """
    auth_data = query_auth_data_from_request(req=req, db=db, only_session_token=True)
    _query_oauth_client(db=db, client_id=client_id)
    oauth_client_user = crud.oauth_client_user.get_by_user_id(
        db, user_id=auth_data.user.id
    )

    return api_success(
        {
            "is_linked": oauth_client_user is not None
            and parse_permissions_from_scope(oauth_client_user.requested_scope)
            == parse_permissions_from_scope(scope),
        }
    )
