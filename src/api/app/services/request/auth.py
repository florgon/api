"""
    Request handler and decoder.
    Allows to query auth data from your token or request.
    Root handler for authentication decode.
"""

from typing import Type

from app.database import crud
from app.database.models.user_session import UserSession
from app.services.api.errors import ApiErrorCode, ApiErrorException
from app.services.permissions import Permission, parse_permissions_from_scope
from app.services.request.auth_data import AuthData
from app.services.request.session_check_client import session_check_client_by_request
from app.tokens.access_token import AccessToken
from app.tokens.base_token import BaseToken
from app.tokens.session_token import SessionToken
from fastapi.requests import Request
from sqlalchemy.orm import Session


def query_auth_data_from_token(
    token: str,
    db: Session,
    *,
    only_session_token: bool = False,
    required_permissions: list[Permission] | None = None,
    allow_deactivated: bool = False,
    allow_external_clients: bool = False,
    request: Request | None = None,
) -> AuthData:
    """
    Queries authentication data from your token.
    :param token: Token itself.
    :param db: Database session.
    :param only_session_token: If true, will query for session token, not access.
    :param required_permissions: If passed, will require permission from token.
    :param allow_deactivated: If true, allow deactivated user to authenticate.
    :param request: Request for the session check (ip, user agent)
    """

    # Decode external token and query auth data from it.
    token_type: Type[BaseToken] = SessionToken if only_session_token else AccessToken
    auth_data = _decode_token(
        token,
        token_type,
        db,
        required_permissions=required_permissions,
        allow_external_clients=allow_external_clients,
        request=request,
    )
    if only_session_token:
        if auth_data.token.get_type() != SessionToken.get_type():
            raise ApiErrorException(
                ApiErrorCode.AUTH_INVALID_TOKEN,
                "Got unexpected token type after decoding! Mostly due to token / server side error!",
            )
    return _query_auth_data(auth_data, db, allow_deactivated)


def query_auth_data_from_request(
    req: Request,
    db: Session,
    *,
    only_session_token: bool = False,
    required_permissions: list[Permission] | None = None,
    allow_deactivated: bool = False,
    allow_external_clients: bool = False,
) -> AuthData:
    """
    Queries authentication data from request (from request token).
    :param req: Request itself.
    :param db: Database session.
    :param only_session_token: If true, will query for session token, not access.
    :param required_permissions: If passed, will require permission from token.
    :param allow_deactivated: If true, allow deactivated user to authenticate.
    """

    # Get token from request and query data from it as external token.
    token = _get_token_from_request(req, only_session_token)
    return query_auth_data_from_token(
        token,
        db,
        only_session_token=only_session_token,
        required_permissions=required_permissions,
        allow_deactivated=allow_deactivated,
        allow_external_clients=allow_external_clients,
        request=req,
    )


def try_query_auth_data_from_request(
    req: Request,
    db: Session,
    *,
    only_session_token: bool = False,
    required_permissions: list[Permission] | None = None,
    allow_deactivated: bool = False,
    allow_external_clients: bool = False,
) -> tuple[bool, AuthData]:
    """
    Tries query authentication data from request (from request token), and returns tuple with status and auth data.
    :param req: Request itself.
    :param db: Database session.
    :param only_session_token: If true, will query for session token, not access.
    :param required_permissions: If passed, will require permission from token.
    :param allow_deactivated: If true, allow deactivated user to authenticate.
    """

    try:
        # Try to authenticate, and if does not fall, return OK.
        auth_data = query_auth_data_from_request(
            req=req,
            db=db,
            only_session_token=only_session_token,
            required_permissions=required_permissions,
            allow_deactivated=allow_deactivated,
            allow_external_clients=allow_external_clients,
        )
        return True, auth_data
    except ApiErrorException:
        # Got exception, not authorized.
        return False, None


def _get_token_from_request(req: Request, only_session_token: bool) -> str:
    """
    Returns token from request.
    :param req: Request itself.
    :param only_session_token: If true, will get session token.
    """
    if only_session_token:
        return req.query_params.get("session_token", "")
    return req.headers.get("Authorization", "") or req.query_params.get(
        "access_token", ""
    )


def _decode_token(
    token: str,
    token_type: Type[BaseToken],
    db: Session,
    required_permissions: list[Permission] | None = None,
    request: Request | None = None,
    allow_external_clients: bool = False,
) -> AuthData:
    """
    Decodes given token, to payload and session.
    :param token: Token to decode.
    :param token_type: Token type to get.
    :param db: Database session.
    :param required_permissions: If passed, will require permission from token.
    """

    if token_type is not AccessToken and token_type is not SessionToken:
        raise ValueError(
            "Unexpected type of the token type inside _decode_token! Should be access or session!"
        )

    if not token:
        raise ApiErrorException(ApiErrorCode.AUTH_REQUIRED, "Authentication required!")

    # Decode base token.
    unsigned_token = token_type.decode_unsigned(token)

    # Checks for token allowance.
    scope = unsigned_token.get_scope() if token_type.get_type() == "access" else ""
    permissions = _query_scope_permissions(scope, required_permissions)

    # Query session, decode with valid signature.
    allow_external_clients = (
        (Permission.noexpire in permissions) if not allow_external_clients else True
    )
    session = _query_session_from_sid(
        unsigned_token.get_session_id(),
        db,
        request,
        allow_external_clients=allow_external_clients,
    )
    signed_token = token_type.decode(token, key=session.token_secret)
    if not signed_token.signature_is_valid():
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN,
            "Token invalid! (Signature validation failed)",
        )

    # Return DTO.
    return AuthData(token=signed_token, session=session, permissions=permissions)


def _query_scope_permissions(
    scope: str, required_permissions: list[Permission] | None
) -> list[Permission]:
    """
    Queries scope permissions with checking required permission.
    :param scope: Scope string (From request).
    :param required_permissions: Permission to require.
    """
    permissions = parse_permissions_from_scope(scope)

    if required_permissions:
        if isinstance(required_permissions, Permission):
            required_permissions = [required_permissions]
        for required_permission in required_permissions:
            if required_permission not in permissions:
                raise ApiErrorException(
                    ApiErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
                    f"Insufficient permissions (required: {required_permission.value})",
                    {"required_scope": required_permission.value},
                )

    return permissions


def _query_session_from_sid(
    session_id: int | None,
    db: Session,
    request: Request | None = None,
    allow_external_clients: bool = False,
) -> UserSession:
    """
    Queries session from SID (session_id).
    :param session_id: SID itself.
    :param db: Database session.
    """

    session = (
        crud.user_session.get_by_id(db, session_id=session_id) if session_id else None
    )

    # Validate session.
    if not session:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Token invalid!")
    if not session.is_active:
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN,
            "Session closed (Token invalid due to session deactivation)!",
        )
    if request is not None and not allow_external_clients:
        session_check_client_by_request(db, session, request)
    return session


def _query_auth_data(
    auth_data: AuthData, db: Session, allow_deactivated: bool
) -> AuthData:
    """
    Finalizes query of  authentication data.
    :param auth_data: Authentication data.
    :param db: Database session.
    :param allow_deactivated: If true, allow deactivated user to authenticate.
    """
    user = crud.user.get_by_id(db=db, user_id=auth_data.token.get_subject())

    # Validate authentication data.
    if not user:
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "User with given token does not exists!",
        )
    if not allow_deactivated and not user.is_active:
        raise ApiErrorException(
            ApiErrorCode.USER_DEACTIVATED, "User account deactivated, access denied!"
        )
    if auth_data.session.owner_id != user.id:
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Token session was linked to another user!"
        )

    # Return modified DTO.
    auth_data.user = user
    return auth_data
