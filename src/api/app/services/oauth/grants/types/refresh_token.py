"""
    Resolves refresh token grant.
"""

from fastapi.responses import JSONResponse
from app.services.tokens import RefreshToken, AccessToken
from app.services.oauth.permissions import (
    permissions_get_ttl,
    parse_permissions_from_scope,
    normalize_scope,
    Permission,
)
from app.services.api import api_success, api_error, ApiErrorCode
from app.schemas.oauth import ResolveGrantModel
from app.database.repositories import (
    UsersRepository,
    UserSessionsRepository,
    OAuthClientsRepository,
)
from app.database.dependencies import Session
from app.config import Settings


def oauth_refresh_token_grant(
    model: ResolveGrantModel, db: Session, settings: Settings
) -> JSONResponse:
    """OAuth refresh token grant type."""
    refresh_token = model.refresh_token
    if not refresh_token:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST,
            "`refresh_token` required for `refresh_token` grant type!",
        )

    refresh_token_unsigned = RefreshToken.decode_unsigned(refresh_token)

    session_id = refresh_token_unsigned.get_session_id()
    session = UserSessionsRepository(db).get_by_id(session_id) if session_id else None
    if not session:
        return api_error(
            ApiErrorCode.AUTH_INVALID_TOKEN,
            "Refresh token has not linked to any session!",
        )

    refresh_token_signed = RefreshToken.decode(refresh_token, key=session.token_secret)  # type: ignore

    if model.client_id != refresh_token_signed.get_client_id():
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_ID_MISMATCH,
            "Given refresh token was obtained with different client!",
        )

    oauth_client = OAuthClientsRepository(db).get_by_id(model.client_id, is_active=True)

    if not oauth_client:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found, deactivated!",
        )

    if oauth_client.secret != model.client_secret:
        return api_error(
            ApiErrorCode.OAUTH_CLIENT_SECRET_MISMATCH,
            "Invalid client_secret! Please review secret, or generate new secret.",
        )

    user = UsersRepository(db).get_user_by_id(
        user_id=refresh_token_signed.get_subject()
    )
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
