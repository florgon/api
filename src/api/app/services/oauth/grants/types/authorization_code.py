"""
    Resolves OAuth code grant.
"""


from dataclasses import dataclass

from fastapi.responses import JSONResponse
from app.services.tokens import RefreshToken, OAuthCode, AccessToken
from app.services.oauth.permissions import (
    permissions_get_ttl,
    parse_permissions_from_scope,
    normalize_scope,
    Permission,
)
from app.services.api import api_success, ApiErrorException, ApiErrorCode
from app.schemas.oauth import ResolveGrantModel
from app.database.repositories import (
    UsersRepository,
    UserSessionsRepository,
    OAuthCodesRepository,
    OAuthClientsRepository,
)
from app.database.models.user_session import UserSession
from app.database.models.user import User
from app.database.dependencies import Session
from app.config import Settings


@dataclass
class TokensPair:
    """Refresh + Access encoded tokens pair."""

    access_ttl: float | int
    access_permissions: set[Permission]
    access_token: str
    refresh_token: str


def _verify_oauth_client_secret(
    db: Session, client_id: int, client_secret: str
) -> None:
    """
    Checks that oauth client is valid for that client secret.
    """
    oauth_client = OAuthClientsRepository(db).get_by_id(client_id, is_active=True)

    if not oauth_client:
        raise ApiErrorException(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )

    if oauth_client.secret != client_secret:
        raise ApiErrorException(
            ApiErrorCode.OAUTH_CLIENT_SECRET_MISMATCH,
            "Invalid client secret! Please review secret, or generate new secret.",
        )


def _query_user_by_user_id(db: Session, session: UserSession, user_id: int) -> User:
    """
    Returns user by ID and verify it by session.
    """
    user = UsersRepository(db).get_user_by_id(user_id=user_id)
    if not user:
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "Unable to find user that belongs to this code!",
        )
    if session.owner_id != user.id:
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Code session was linked to another user!"
        )
    return user


def _verify_oauth_params(code_token: OAuthCode, redirect_uri: str, client_id: int):
    """
    Checks resolve oauth params.
    """
    if redirect_uri != code_token.get_redirect_uri():  # pylint: disable=no-member
        raise ApiErrorException(
            ApiErrorCode.OAUTH_CLIENT_REDIRECT_URI_MISMATCH,
            "redirect_uri should be same!",
        )

    if client_id != code_token.get_client_id():  # pylint: disable=no-member
        raise ApiErrorException(
            ApiErrorCode.OAUTH_CLIENT_ID_MISMATCH,
            "Given code was obtained with different client!",
        )


def _decode_signed_code_token_with_session(
    db: Session, raw_code_token: str
) -> tuple[OAuthCode, UserSession]:
    """
    Returns decoded code token and session.
    """
    code_token_unsigned = OAuthCode.decode_unsigned(raw_code_token)

    session_id = code_token_unsigned.get_session_id()  # pylint: disable=no-member
    session = UserSessionsRepository(db).get_by_id(session_id) if session_id else None
    if not session:
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Code has not linked to any session!"
        )

    code_token = OAuthCode.decode(raw_code_token, key=session.token_secret)  # type: ignore
    return code_token, session


def _verify_and_expire_oauth_code(db: Session, code_token: OAuthCode) -> None:
    """
    Verifies and expires oauth code by query database code.
    """
    oauth_code = OAuthCodesRepository(db).get_by_id(code_token.get_code_id())
    if not oauth_code:
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN, "No additional information."
        )
    if oauth_code.was_used:
        raise ApiErrorException(
            ApiErrorCode.AUTH_EXPIRED_TOKEN, "Code has been expired or already used!"
        )
    oauth_code.was_used = True  # type: ignore
    db.commit()


def _query_user_data_from_raw_code_token(
    db: Session,
    raw_code_token: str,
    redirect_uri: str,
    client_id: int,
    client_secret: str,
) -> tuple[OAuthCode, UserSession, User]:
    """
    Returns user data from raw code token by decoding and veryfing it.
    """

    code_token, session = _decode_signed_code_token_with_session(db, raw_code_token)
    _verify_oauth_params(code_token, redirect_uri, client_id)
    _verify_oauth_client_secret(db, client_id=client_id, client_secret=client_secret)
    user = _query_user_by_user_id(db, session, user_id=code_token.get_subject())
    _verify_and_expire_oauth_code(db, code_token)
    return code_token, session, user


def encode_tokens_pair(
    code_token: OAuthCode, session: UserSession, user: User, settings: Settings
) -> TokensPair:
    """
    Returns encoded tokens pair.
    """
    # Access token have infinity TTL, if there scope permission for no expiration date.
    access_token_permissions = parse_permissions_from_scope(
        code_token.get_scope()  # pylint: disable=no-member
    )

    access_token_ttl = permissions_get_ttl(
        access_token_permissions, default_ttl=settings.security_access_tokens_ttl
    )

    access_token = AccessToken(
        settings.security_tokens_issuer,
        access_token_ttl,
        user.id,  # type: ignore
        session.id,  # type: ignore
        normalize_scope(code_token.get_scope()),  # pylint: disable=no-member
    ).encode(
        key=session.token_secret  # type: ignore
    )
    refresh_token = RefreshToken(
        settings.security_tokens_issuer,
        settings.security_refresh_tokens_ttl,
        user.id,  # type: ignore
        session.id,  # type: ignore
    ).encode(
        key=session.token_secret  # type: ignore
    )

    return TokensPair(
        access_ttl=access_token_ttl,
        access_permissions=access_token_permissions,
        access_token=access_token,
        refresh_token=refresh_token,
    )


def oauth_authorization_code_grant(
    model: ResolveGrantModel,
    db: Session,
    settings: Settings,
) -> JSONResponse:
    """OAuth authorization code grant type."""
    if not model.code:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "`code` required for `authorization_code` grant type!",
        )
    if not model.redirect_uri:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "`redirect_uri` required for `authorization_code` grant type!",
        )
    code_token, session, user = _query_user_data_from_raw_code_token(
        db=db,
        raw_code_token=model.code,
        redirect_uri=model.redirect_uri,
        client_id=model.client_id,
        client_secret=model.client_secret,
    )

    tokens_pair = encode_tokens_pair(code_token, session, user, settings)
    send_email_field = Permission.email in tokens_pair.access_permissions
    return api_success(
        {
            "access_token": tokens_pair.access_token,
            "refresh_token": tokens_pair.refresh_token,
            "expires_in": tokens_pair.access_ttl,
            "user_id": user.id,
        }
        | ({"email": user.email} if send_email_field else {})
    )
