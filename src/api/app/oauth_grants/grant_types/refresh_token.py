"""
    Resolves refresh token grant.
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
from app.tokens import AccessToken, RefreshToken

# Libraries.
from fastapi import Request
from fastapi.responses import JSONResponse


def oauth_refresh_token_grant(
    req: Request, client_id: int, client_secret: str, db: Session, settings: Settings
) -> JSONResponse:
    """OAuth refresh token grant type."""
    refresh_token = req.query_params.get("refresh_token", None)
    if not refresh_token:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`refresh_token` required for `refresh_token` grant type!",
        )

    refresh_token_unsigned = RefreshToken.decode_unsigned(refresh_token)

    session_id = refresh_token_unsigned.get_session_id()  # pylint: disable=no-member
    session = (
        crud.user_session.get_by_id(db, session_id=session_id) if session_id else None
    )
    if not session:
        return api_error(
            ApiErrorCode.AUTH_INVALID_TOKEN,
            "Refresh token has not linked to any session!",
        )

    refresh_token_signed = RefreshToken.decode(refresh_token, key=session.token_secret)

    if client_id != refresh_token_signed.get_client_id():  # pylint: disable=no-member
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_ID_MISMATCH,
            "Given refresh token was obtained with different client!",
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
    user = crud.user.get_by_id(db=db, user_id=refresh_token_signed.get_subject())
    if not user:
        return api_error(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "Unable to find user that belongs to this refresh token!",
        )
    if session.owner_id != user.id:
        return api_error(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Token session was linked to another user!"
        )

    # Access token have infinity TTL, if there is scope permission given for no expiration date.
    access_token_permissions = parse_permissions_from_scope(
        refresh_token_signed.get_scope()  # pylint: disable=no-member
    )

    access_token_ttl = permissions_get_ttl(
        access_token_permissions, default_ttl=settings.security_access_tokens_ttl
    )

    access_token = AccessToken(
        settings.security_tokens_issuer,
        access_token_ttl,
        user.id,
        session.id,
        normalize_scope(refresh_token_signed.get_scope()),  # pylint: disable=no-member
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
