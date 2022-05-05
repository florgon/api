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


def try_decode_token_from_request(req: Request, jwt_secret: str) -> tuple[bool, JSONResponse, str]:
    """ Tries to get and decode auth JWT token from request """
    # Get token from request.
    token = req.query_params.get("token") or req.headers.get("Authorization")
    if not token:
        return False, api_error(ApiErrorCode.AUTH_REQUIRED, "Authentication required!"), token

    # Decode token.
    try:
        token_payload = jwt.decode(token, jwt_secret)
    except jwt.jwt.exceptions.InvalidSignatureError:
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token has invalid signature!"), token
    except jwt.jwt.exceptions.ExpiredSignatureError:
        return False, api_error(ApiErrorCode.AUTH_EXPIRED_TOKEN, "Token has been expired!"), token
    except jwt.jwt.exceptions.PyJWTError:
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token invalid!"), token

    # All ok, return JWT payload.
    return True, token_payload, token

def try_query_user_from_request(req: Request, db: Session, jwt_secret: str) -> tuple[bool, JSONResponse, str]:
    """ Tries to get and decode user from JWT token from request """

    # Try authenticate.
    is_authenticated, token_payload_or_error, token = try_decode_token_from_request(req, jwt_secret)
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