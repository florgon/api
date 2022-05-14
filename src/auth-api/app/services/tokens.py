"""
    JSON Web Tokens service.
"""

from . import jwt


def encode_session_jwt_token(user, issuer: str, ttl: int, secret: str) -> str:
    payload = {
        "type": "session"
    }
    return jwt.encode(user, payload, issuer, ttl, secret)


def encode_access_jwt_token(user, issuer: str, ttl: int, secret: str) -> str:
    payload = {
        "type": "access",
        "_user": {
            "username": user.username
        }
    }
    return jwt.encode(user, payload, issuer, ttl, secret)

def try_decode_access_jwt_token(token: str, secret: str) -> dict:
    return jwt.try_decode(token=token, secret=secret, _token_type="access")

def try_decode_session_jwt_token(token: str, secret: str) -> dict:
    return jwt.try_decode(token=token, secret=secret, _token_type="session")
