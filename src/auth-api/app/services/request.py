"""
    Utils for working with request.
"""

# Libraries.
from fastapi import Request
from fastapi.responses import JSONResponse

# Services.
from app.services import jwt, cftokens
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
