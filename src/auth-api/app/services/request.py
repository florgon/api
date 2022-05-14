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
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error


def try_decode_token_from_request(req: Request, jwt_secret: str, *, allow_session_token: bool = False) -> tuple[bool, JSONResponse, str]:
    """ Tries to get and decode auth JWT token from request """
    # Get token from request.
    token = req.headers.get("Authorization") or req.query_params.get("token") or req.query_params.get("access_token")

    if not token:
        if allow_session_token:
            session_token = req.query_params.get("session_token")
            if session_token:
                return jwt.try_decode(session_token, jwt_secret, _token_type="session")
        return False, api_error(ApiErrorCode.AUTH_REQUIRED, "Authentication required!"), token
    return jwt.try_decode(token, jwt_secret, _token_type="access")

def try_query_user_from_request(req: Request, db: Session, jwt_secret: str, *, allow_session_token: bool = False) -> tuple[bool, JSONResponse, str]:
    """ Tries to get and decode user from JWT token from request """

    # Try authenticate.
    is_authenticated, token_payload_or_error, token = try_decode_token_from_request(req, jwt_secret, allow_session_token=allow_session_token)
    if not is_authenticated:
        return False, token_payload_or_error, token
    token_payload = token_payload_or_error

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])

    # Check that user exists.
    if not user:
        return False, api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "User with given token does not exists!"), token_payload

    # All.
    return True, user, token_payload