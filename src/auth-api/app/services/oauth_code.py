"""
    JSON Web Tokens service.
"""

from . import jwt

# Services.
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error

def encode_oauth_jwt_code(user, client_id: int, redirect_uri: str, scope: str, issuer: str, ttl: int, secret: str) -> str:
    payload = {
        "type": "code",
        "scope": scope,
        "redirect_uri": redirect_uri,
        "client_id": client_id
    }
    return jwt.encode(user, payload, issuer, ttl, secret)

def try_decode_oauth_jwt_code(token: str, secret: str) -> dict:
    try:
        token_payload = jwt.decode(token, secret)
    except jwt.jwt.exceptions.InvalidSignatureError:
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Code has invalid signature!"), token
    except jwt.jwt.exceptions.ExpiredSignatureError:
        return False, api_error(ApiErrorCode.AUTH_EXPIRED_TOKEN, "Code has been expired!"), token
    except jwt.jwt.exceptions.PyJWTError:
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Code invalid!"), token

    if token_payload.get("type") != "code":
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token has invalid type!"), token

    # All ok, return JWT payload.
    return True, token_payload, token