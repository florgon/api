"""
    JSON Web Tokens service.
"""

# JWT libraries.
import time
import jwt

# Services.
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error

# Base JWT algorithm, not required to be changed by you,
# may be changed to RS256 later....
JWT_ALGORITHM = "HS256"


def encode(user, payload: dict, issuer: str, ttl: int, secret: str) -> str:
    """ Encodes user object inside JWT token. """

    # Serialize user for token.
    token_issued_at = time.time()
    token_payload = {
        "iss": issuer,
        "sub": user.id,

        "iat": token_issued_at,
        "exp": token_issued_at + ttl,
        
        **payload
    }

    token = jwt.encode(token_payload, secret, algorithm=JWT_ALGORITHM)
    return token


def decode(token: str, secret: str) -> dict:
    """ Returns is given token valid and its payload. """
    token_payload = jwt.decode(token, secret, algorithms=JWT_ALGORITHM)
    return token_payload


def try_decode(token: str, secret: str, *, _token_type: str) -> dict:
    # Decode token.
    try:
        token_payload = decode(token, secret)
    except jwt.exceptions.InvalidSignatureError:
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token has invalid signature!"), token
    except jwt.exceptions.ExpiredSignatureError:
        return False, api_error(ApiErrorCode.AUTH_EXPIRED_TOKEN, "Token has been expired!"), token
    except jwt.exceptions.PyJWTError:
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token invalid!"), token

    if token_payload.get("type") != _token_type:
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token has invalid type!"), token

    # All ok, return JWT payload.
    return True, token_payload, token
