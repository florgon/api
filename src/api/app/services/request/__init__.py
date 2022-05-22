"""
    Request handler and decoder.
    Allows to query auth data from your token or request.
    Root handler for authentication decode.
"""

from sqlalchemy.orm import Session
from fastapi import Request

from app.database import crud
from app.services import jwt
from app.services.permissions import Permissions, parse_permissions_from_scope
from app.services.api.errors import ApiErrorCode, ApiErrorException

from app.database.models.user import User
from app.database.models.user_session import UserSession


class AuthData(object):
    """ DTO for authenticated request."""

    user: User
    token_payload: dict
    session: UserSession
    permissions: Permissions | None

    def __init__(self, token_payload: str, session: UserSession, \
        user: User | None = None, permissions: Permissions | None = None) -> None:
        """
            :param user: User database model object.
            :param token_payload: Decoded token payload.
            :param session: User session database model object.
        """
        self.user = user
        self.token_payload = token_payload
        self.session = session

        # Parse permission once.
        self.permissions = permissions if permissions else parse_permissions_from_scope(token_payload.get("scope", ""))


def query_auth_data_from_token(token: str, db: Session, *, \
    only_session_token: bool = False, 
    required_permissions: Permissions | None = None,
    allow_deactivated: bool = False
    ) -> AuthData:
    """
        Queries authentication data from your token.
        :param token: Token itself.
        :param db: Database session.
        :param only_session_token: If true, will query for session token, not access.
        :param required_permissions: If passed, will require permission from token.
        :param allow_deactivated: If true, allow deactivated user to authenticate.
    """

    # Decode external token and query auth data from it.
    token_type = "session" if only_session_token else "access"
    auth_data = _decode_token(
        token, token_type, db,
        required_permissions=required_permissions
    )
    return _query_auth_data(auth_data, db, allow_deactivated)


def query_auth_data_from_request(req: Request, db: Session, *, \
    only_session_token: bool = False, required_permissions: Permissions | None = None, allow_deactivated: bool = False
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
        token, db, 
        only_session_token=only_session_token, 
        required_permissions=required_permissions, 
        allow_deactivated=allow_deactivated
    )


def _get_token_from_request(req: Request, only_session_token: bool) -> str:
    """
        Returns token from request.
        :param req: Request itself.
        :param only_session_token: If true, will get session token.
    """
    if only_session_token:
        return req.query_params.get("session_token")
    return req.headers.get("Authorization") or req.query_params.get("access_token")


def _decode_token(token: str, token_type: str, db: Session, \
    required_permissions: Permissions | None = None) -> AuthData:
    """
        Decodes given token, to it payload and session.
        :param token: Token to decode.
        :param token_type: Token type to get.
        :param db: Database session.
        :param required_permissions: If passed, will require permission from token.
    """
    
    # Decode without verifying signature, to query session, and then
    # decode with session token secret, with veryfing user token identity signature.
    token_payload = jwt.decode(token, None, _token_type=token_type)
    session = _query_session_from_sid(token_payload.get("sid", None), db)
    token_payload = jwt.decode(token, session.token_secret, _token_type=token_type)

    # Checks for token allowance.
    permissions = _query_scope_permissions(token_payload.get("scope", ""), required_permissions)

    # Return DTO.
    return AuthData(
        token_payload=token_payload,
        session=session,
        permissions=permissions
    )


def _query_scope_permissions(scope: str, required_permissions: Permissions | None) -> None:
    """
        Queries scope permissions with checking required permission.
        :param scope: Scope string (From request).
        :param required_permissions: Permission to require.
    """
    permissions = parse_permissions_from_scope(scope)

    if required_permissions:
        for required_permission in required_permissions:
            if required_permission not in permissions:
                raise ApiErrorException(
                    ApiErrorCode.AUTH_INSUFFICIENT_PERMISSSIONS, 
                    f"Insufficient permissions (required: {required_permission.value})", 
                    {"required_scope": required_permission.value})

    return permissions


def _query_session_from_sid(session_id: int | None, db: Session) -> UserSession:
    """
        Queries session from SID (session_id).
        :param session_id: SID itself.
        :param db: Database sesion.
    """

    session = crud.user_session.get_by_id(db, session_id=session_id) if session_id else None

    # Validate session.
    if not session:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Token invalid!")
    if not session.is_active:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Session closed (Token invalid due to session deactivation)!")

    return session


def _query_auth_data(auth_data: AuthData, \
    db: Session, allow_deactivated: bool) -> AuthData:
    """
        Queries authentication data from token payload and session.
        :param token_payload: Payload of authentication token.
        :param session: User session.
        :param db: Database session.
        :param allow_deactivated: If true, allow deactivated user to authenticate.
    """
    user = crud.user.get_by_id(db=db, user_id=auth_data.token_payload["sub"])

    # Validate authentication data.
    if not user:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "User with given token does not exists!")
    if not allow_deactivated and not user.is_active:
        raise ApiErrorException(ApiErrorCode.USER_DEACTIVATED, "User account deactivated, access denied!")
    if auth_data.session.owner_id != user.id:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Token session was linked to another user!")
    
    # Return modified DTO.
    auth_data.user = user
    return auth_data