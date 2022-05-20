"""
    Utils for working with request.
"""

# Libraries.
from sqlalchemy.orm import Session
from fastapi import Request
from fastapi.responses import JSONResponse

# Services.
from app.database import crud
from app.services import jwt
from app.services.permissions import Permission, parse_permissions_from_scope
from app.services.api.errors import ApiErrorCode, ApiErrorException
from app.database.models.user import User
from app.database.models.user_session import UserSession


def _decode_token_from_request(db: Session, req: Request, *, \
    only_session_token: bool = False, 
    required_permission: Permission | None = None) -> tuple[dict, UserSession]:
    """ Decode auth JWT token from request """

    if only_session_token:
        token_type = "session"
        token = req.query_params.get("session_token")
    else:
        token_type = "access"
        token = req.headers.get("Authorization") or req.query_params.get("token") or req.query_params.get("access_token")
    if not token:
        raise ApiErrorException(ApiErrorCode.AUTH_REQUIRED, "Auth required")
    token_payload = jwt.decode(token, None, _token_type=token_type)

    # Query session.
    session_id = token_payload.get("sid", None)
    session = crud.user_session.get_by_id(db, session_id=session_id) if session_id else None
    if not session:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Token invalid!")

    # Decode with session token.
    token_payload = jwt.decode(token, session.token_secret, _token_type=token_type)

    # Scopes.
    if required_permission:
        permissions = parse_permissions_from_scope(token_payload["scope"])
        if required_permission not in permissions:
            raise ApiErrorException(ApiErrorCode.AUTH_INSUFFICIENT_PERMISSSIONS, f"Insufficient permissions (required: {required_permission.value})", {
                "required_scope": required_permission.value
            })
    return token_payload, session

def query_auth_data_from_request(req: Request, db: Session, *, \
    only_session_token: bool = False, 
    required_permission: Permission | None = None,
    allow_deactivated: bool = False
    ) -> tuple[User, dict, UserSession]:
    """ Decode user and session from JWT token from request """

    token_payload, session = _decode_token_from_request(
        db, req, 
        only_session_token=only_session_token, 
        required_permission=required_permission
    )

    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])

    if not user:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "User with given token does not exists!")

    if not allow_deactivated and not user.is_active:
        raise ApiErrorException(ApiErrorCode.USER_DEACTIVATED, "User account deactivated, access denied!")

    if session.owner_id != user.id:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Token session was linked to another user!")

    return user, token_payload, session