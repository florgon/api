"""
    JSON Web Tokens service.
"""

from . import jwt


def encode_session_jwt_token(user, session, issuer: str, ttl: int) -> str:
    payload = {
        "typ": "session",
        "sid": session.id
    }
    return jwt.encode(user, payload, issuer, ttl, session.token_secret)


def encode_access_jwt_token(user, session, nscope: str, issuer: str, ttl: int) -> str:
    payload = {
        "typ": "access",
        "sid": session.id,
        "scope": nscope,
    }
    return jwt.encode(user, payload, issuer, ttl, session.token_secret)

def try_decode_access_jwt_token(token: str, secret: str) -> tuple:
    return jwt.try_decode(token=token, secret=secret, _token_type="access")

def try_decode_session_jwt_token(token: str, secret: str | None = None) -> tuple:
    return jwt.try_decode(token=token, secret=secret, _token_type="session")
