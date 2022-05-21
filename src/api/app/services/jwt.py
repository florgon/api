"""
    JSON Web Tokens service.
"""

import time
import jwt

from app.services.api.errors import ApiErrorCode, ApiErrorException

# Base JWT algorithm, not required to be changed by you,
# may be changed to RS256 later....
JWT_ALGORITHM = "HS256"


def encode(user, payload: dict, issuer: str, ttl: int, secret: str) -> str:
    """ Encodes user object inside JWT token. """

    # Serialize user for token.
    token_issued_at = time.time()
    token_payload = {
        # Hostname of the token issuer.
        "iss": issuer,
        # Token subject (user index)
        "sub": user.id,
        # Timestamp when token is created.
        "iat": token_issued_at,

        **payload
    }

    if ttl > 0:
        # If time-to-live (TTL) is not null,
        # set token expiration date, which is constructed by 
        # time when token was created (now) (timestamp, in seconds) and adding it TTL in seconds.
        token_payload["exp"] = token_issued_at + ttl

    token = jwt.encode(token_payload, secret, algorithm=JWT_ALGORITHM)
    return token


def decode(token: str, secret: str | None = None, *, _token_type: str) -> dict:
    """ Returns token payload. """
    try:
        token_payload = jwt.decode(token, secret, algorithms=JWT_ALGORITHM, options={
            "verify_signature": (secret is not None)
        })
    except jwt.exceptions.InvalidSignatureError:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Token has invalid signature!")
    except jwt.exceptions.ExpiredSignatureError:
        raise ApiErrorException(ApiErrorCode.AUTH_EXPIRED_TOKEN, "Token has been expired!")
    except jwt.exceptions.PyJWTError:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Token invalid!")

    if token_payload.get("typ", "") != _token_type:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Token has wrong type!")

    return token_payload