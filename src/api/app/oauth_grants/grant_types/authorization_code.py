"""
    Resolves OAuth code grant.
"""

from app.config import Settings
from app.database import crud
from app.database.dependencies import Session
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success

# Services.
from app.services.permissions import (
    Permission,
    normalize_scope,
    parse_permissions_from_scope,
    permissions_get_ttl,
)
from app.tokens import AccessToken
from app.tokens import RefreshToken

# Other.
from app.tokens import OAuthCode

# Libraries.
from fastapi import Request
from fastapi.responses import JSONResponse


def oauth_authorization_code_grant(
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

    session_id = code_unsigned.get_session_id()  # pylint: disable=no-member
    session = (
        crud.user_session.get_by_id(db, session_id=session_id) if session_id else None
    )
    if not session:
        return api_error(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Code has not linked to any session!"
        )

    code_signed = OAuthCode.decode(code, key=session.token_secret)

    if redirect_uri != code_signed.get_redirect_uri():  # pylint: disable=no-member
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_REDIRECT_URI_MISMATCH,
            "redirect_uri should be same!",
        )

    if client_id != code_signed.get_client_id():  # pylint: disable=no-member
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
            ApiErrorCode.AUTH_INVALID_TOKEN, "Code session was linked to another user!"
        )

    # Access token have infinity TTL, if there is scope permission given for no expiration date.
    access_token_permissions = parse_permissions_from_scope(
        code_signed.get_scope()  # pylint: disable=no-member
    )

    access_token_ttl = permissions_get_ttl(
        access_token_permissions, default_ttl=settings.security_access_tokens_ttl
    )

    access_token = AccessToken(
        settings.security_tokens_issuer,
        access_token_ttl,
        user.id,
        session.id,
        normalize_scope(code_signed.get_scope()),  # pylint: disable=no-member
    ).encode(key=session.token_secret)
    refresh_token = RefreshToken(
        settings.security_tokens_issuer,
        settings.security_refresh_tokens_ttl,
        user.id,
        session.id,
    ).encode(key=session.token_secret)

    response_payload = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": access_token_ttl,
        "user_id": user.id,
    }

    if Permission.email in access_token_permissions:
        response_payload["email"] = user.email

    return api_success(response_payload)
