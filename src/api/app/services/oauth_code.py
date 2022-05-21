"""
    JSON Web Tokens service.
"""

from . import jwt

from app.services.api.errors import ApiErrorCode, ApiErrorException

def encode_oauth_jwt_code(user, session, client_id: int, redirect_uri: str, scope: str, issuer: str, ttl: int) -> str:
    payload = {
        "typ": "code",
        "sid": session.id,
        "scope": scope,
        "ruri": redirect_uri,
        "cid": client_id
    }
    return jwt.encode(user, payload, issuer, ttl, session.token_secret)

def decode_oauth_jwt_code(token: str, secret: str | None = None) -> dict:
    try:
        token_payload = jwt.decode(token, secret, _token_type="code")
    except jwt.jwt.exceptions.InvalidSignatureError:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Code has invalid signature!")
    except jwt.jwt.exceptions.ExpiredSignatureError:
        raise ApiErrorException(ApiErrorCode.AUTH_EXPIRED_TOKEN, "Code has been expired!")
    except jwt.jwt.exceptions.PyJWTError:
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Code invalid!")

    if token_payload.get("typ") != "code":
        raise ApiErrorException(ApiErrorCode.AUTH_INVALID_TOKEN, "Code has wrong type!")

    return token_payload