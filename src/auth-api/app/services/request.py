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
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error


def _try_decode_token_from_request(db: Session, req: Request, *, \
    allow_session_token: bool = False, required_permission: Permission | None = None) -> tuple[bool, JSONResponse | dict, str, object | None]:
    """ Tries to get and decode auth JWT token from request """
    # Get token from request.
    token = req.headers.get("Authorization") or req.query_params.get("token") or req.query_params.get("access_token")

    if not token:
        if allow_session_token:
            session_token = req.query_params.get("session_token")
            if session_token:
                is_valid, token_payload_or_error, token = jwt.try_decode(session_token, None, _token_type="session")
                if not is_valid:
                    return False, token_payload_or_error, token, None
                session_id = token_payload_or_error.get("sid", None)
                session = crud.user_session.get_by_id(db, session_id=session_id) if session_id else None
                if not session:
                    return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token has not linked to any session!"), token, session
                return jwt.try_decode(session_token, session.token_secret, _token_type="session"), token, session
        return False, api_error(ApiErrorCode.AUTH_REQUIRED, "Authentication required!"), token, None

    is_valid, token_payload_or_error, token = jwt.try_decode(token, None, _token_type="access")
    if not is_valid:
        return False, token_payload_or_error, token, None
    session_id = token_payload_or_error.get("sid", None)
    session = crud.user_session.get_by_id(db, session_id=session_id) if session_id else None
    if not session:
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token has not linked to any session!"), False, session
    is_authenticated, token_payload_or_error, token = jwt.try_decode(token, session.token_secret, _token_type="access")
    if not is_authenticated:
        return is_authenticated, token_payload_or_error, token, session

    token_payload = token_payload_or_error
    if required_permission:
        permissions = parse_permissions_from_scope(token_payload["scope"])
        if required_permission not in permissions:
            return False, api_error(ApiErrorCode.AUTH_INSUFFICIENT_PERMISSSIONS, f"Insufficient permissions (required: {required_permission.value})", {
                "required_scope": required_permission.value
            }), token, session
    return is_authenticated, token_payload_or_error, token, session

def try_query_user_from_request(req: Request, db: Session, *, \
    allow_session_token: bool = False, required_permission: Permission | None = None) -> tuple[bool, JSONResponse, str]:
    """ Tries to get and decode user from JWT token from request """

    # Try authenticate.
    is_authenticated, token_payload_or_error, token, session = _try_decode_token_from_request(db, req, allow_session_token=allow_session_token, required_permission=required_permission)
    if not is_authenticated:
        return False, token_payload_or_error, token
    token_payload = token_payload_or_error

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])

    # Check that user exists.
    if not user:
        return False, api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "User with given token does not exists!"), token_payload
    if session.owner_id != user.id:
        return api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token session was linked to another user!")

    # All.
    return True, user, token_payload