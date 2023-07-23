"""
    Request handler and decoder.
    Allows to query auth data from your token or request.
    Root handler for authentication decode.
"""

from typing import Type, NoReturn
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi import Depends
from app.services.tokens import SessionToken, BaseToken, AccessToken
from app.services.request.session_check_client import session_check_client_by_request
from app.services.request.auth_data import AuthData
from app.services.permissions import parse_permissions_from_scope, Permission
from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.database.models.user_session import UserSession
from app.database.dependencies import get_db
from app.database import crud
from app.config import get_logger


class AuthDataDependency:
    """
    FastAPI dependency to query auth data.
    """

    def __init__(
        self,
        *,
        only_session_token: bool = False,
        required_permissions: set[Permission] | None = None,
        allow_deactivated: bool = False,
        allow_external_clients: bool = False,
        trigger_online_update: bool = True,
    ):
        self.kwargs = {
            "only_session_token": only_session_token,
            "required_permissions": required_permissions,
            "allow_deactivated": allow_deactivated,
            "allow_external_clients": allow_external_clients,
            "trigger_online_update": trigger_online_update,
        }

    def __call__(self, req: Request, db: Session = Depends(get_db)):
        return query_auth_data_from_request(req=req, db=db, **self.kwargs)  # type: ignore


def query_auth_data_from_token(
    token: str,
    db: Session,
    *,
    only_session_token: bool = False,
    required_permissions: set[Permission] | None = None,
    allow_deactivated: bool = False,
    allow_external_clients: bool = False,
    trigger_online_update: bool = True,
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
    if only_session_token and auth_data.token.get_type() != SessionToken.get_type():
        _raise_integrity_check_error()
    return _query_auth_data(
        auth_data,
        db,
        allow_deactivated=allow_deactivated,
        trigger_online_update=trigger_online_update,
    )


def query_auth_data_from_request(
    req: Request,
    db: Session,
    *,
    only_session_token: bool = False,
    required_permissions: set[Permission] | None = None,
    allow_deactivated: bool = False,
    allow_external_clients: bool = False,
    trigger_online_update: bool = True,
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
    token = get_token_from_request(req, only_session_token)
    return query_auth_data_from_token(
        token,
        db,
        only_session_token=only_session_token,
        required_permissions=required_permissions,
        allow_deactivated=allow_deactivated,
        allow_external_clients=allow_external_clients,
        trigger_online_update=trigger_online_update,
        request=req,
    )


def try_query_auth_data_from_request(
    req: Request,
    db: Session,
    *,
    only_session_token: bool = False,
    required_permissions: set[Permission] | None = None,
    allow_deactivated: bool = False,
    allow_external_clients: bool = False,
) -> AuthData | None:
    """
    Tries query authentication data from request (from request token), and returns tuple with status and auth data.
    :param req: Request itself.
    :param db: Database session.
    :param only_session_token: If true, will query for session token, not access.
    :param required_permissions: If passed, will require permission from token.
    :param allow_deactivated: If true, allow deactivated user to authenticate.
    """

    try:
        return query_auth_data_from_request(
            req=req,
            db=db,
            only_session_token=only_session_token,
            required_permissions=required_permissions,
            allow_deactivated=allow_deactivated,
            allow_external_clients=allow_external_clients,
        )
    except ApiErrorException:
        # Any exception occurred - unable to authorize.
        return None


def get_token_from_request(req: Request, only_session_token: bool) -> str:
    """
    Returns token from request.
    :param req: Request itself.
    :param only_session_token: If true, will get only session token.
    """

    if only_session_token:
        # If we are requested to get only session token.

        # Session token not expected to be as header, return just params check.
        return req.query_params.get("session_token", "")

    # Simple access token located in header and params.
    # Notice that if user gives header and param, header should taken and param should skiped!
    token_header = req.headers.get("Authorization", "")
    token_param = req.query_params.get("access_token", "")
    return token_header or token_param


def _decode_token(
    token: str,
    token_type: Type[BaseToken],
    db: Session,
    required_permissions: set[Permission] | None = None,
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
        True if allow_external_clients else Permission.noexpire in permissions
    )
    session = _query_session_from_sid(
        unsigned_token.get_session_id(),
        db,
        request,
        allow_external_clients=allow_external_clients,
    )
    signed_token = token_type.decode(token, key=session.token_secret)  # type: ignore
    if not signed_token.signature_is_valid():
        # If there is invalid signature on the token,
        # means token signed with another user, or old signature...
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN,
            "Unable to validate signature of the token!",
        )

    # Return DTO.
    return AuthData(token=signed_token, session=session, permissions=permissions)


def _query_scope_permissions(
    scope: str, required_permissions: set[Permission] | Permission | None = None
) -> set[Permission]:
    """
    Queries scope permissions with checking required permission (if passed).
    :param scope: Scope string (From request).
    :param required_permissions: Permissions to require, or just one permission, or no permissions.
    """
    permissions = parse_permissions_from_scope(scope)

    if not required_permissions:
        # If no permissions that should be required,
        # simply return parsed permissions.
        return permissions

    if isinstance(required_permissions, Permission):
        # If specified only one permission,
        # convert it to set as expected.
        required_permissions = {required_permissions}

    # Filter scope permissions, and build set with only those permissions that not satisfied.
    if unsatisfied_permissions := set(
        filter(lambda permission: permission not in permissions, required_permissions)
    ):
        # If we have any permission that not satisfied.

        # String of scope of required permissions.
        required_scope = ", ".join(
            [permission.value for permission in unsatisfied_permissions]
        )

        raise ApiErrorException(
            ApiErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            f"Insufficient permissions to call this method! (required scope permissions: {required_scope})",
            {"required_scope": required_scope},
        )

    return permissions


def _query_session_from_sid(
    session_id: int,
    db: Session,
    request: Request | None = None,
    allow_external_clients: bool = False,
) -> UserSession:
    """
    Queries session from SID (session_id).
    :param session_id: Session ID itself (SID).
    :param db: Database session.
    :param request: Request for client check.
    :param allow_external_clients: If false (default) will block all requests from suspicious devices.
    """

    if not isinstance(session_id, int):
        # Internal authentication system integrity check.
        _raise_integrity_check_error()

    session = crud.user_session.get_by_id(db, session_id=session_id)
    if not session:
        # Internal authentication system integrity check.
        # users should never be deleted and this should never happen.
        _raise_integrity_check_error()

    if not session.is_active:
        # If session is not active anymore,
        # means user closed (logouted) or whatever else happened.
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN,
            "Token is not usable as session was closed!",
        )

    if not allow_external_clients and request is not None:
        # If we are not expected to allow external clients (devices),
        # trigger session suspicious check.
        # this will disallow all suspicious devices that are different from session owner device.
        session_check_client_by_request(db, session, request)

    return session


def _query_auth_data(
    auth_data: AuthData,
    db: Session,
    allow_deactivated: bool = False,
    trigger_online_update: bool = True,
) -> AuthData:
    """
    Finalizes query of authentication data by query final user object.
    :param auth_data: Authentication data DTO.
    :param db: Database session.
    :param allow_deactivated: If false, will raise API error for users that deactivated.
    :param trigger_online_update: If true, will trigger online update for user.
    """

    # Query database for our user to feed into auth data DTO.
    user_id = auth_data.token.get_subject()
    user = crud.user.get_by_id(db=db, user_id=user_id)

    if not user or auth_data.session.owner_id != user.id:
        # Internal authentication system integrity check.
        # users should never be deleted and this should never happen.
        _raise_integrity_check_error()

    if not user.is_active and not allow_deactivated:
        # If user is deactivated (banned), and we are not allowed to return with deactivated users,
        # return API error means deactivated user have no permissions to call requested method.
        raise ApiErrorException(
            ApiErrorCode.USER_DEACTIVATED,
            "User account currently deactivated and this method does not allow deactivated users!",
        )

    if trigger_online_update:
        # If this flag is true, means that we should do update of the online time for user.
        # By default, this flag is enabled, means if you want to externally disable this trigger,
        # you should know that this is external trigger.

        # Do update of the online time for user.
        user.time_online = datetime.now()  # type: ignore
        db.commit()

    # Return modified DTO with user ORM model instance.
    auth_data.user = user
    return auth_data


def _raise_integrity_check_error() -> NoReturn:
    """
    Raises authentication system integrity check error.
    """
    get_logger().info(
        "[core_auth] Got catched authentication system integrity check failure!"
    )
    raise ApiErrorException(
        ApiErrorCode.AUTH_INVALID_TOKEN,
        "Authentication system integrity check failed!",
    )
