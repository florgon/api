"""
    JSON Web Tokens service.
"""

# JWT libraries.
import time
import jwt

# Base JWT algorithm, not required to be changed by you,
# may be changed to RS256 later....
JWT_ALGORITHM = "HS256"


def encode(user, issuer: str, ttl: int, secret: str) -> str:
    """ Encodes user object inside JWT token. """

    # Serialize user for token.
    token_issued_at = time.time()
    token_payload = {
        "sub": user.id,
        "iat": token_issued_at,
        "iss": issuer,
        "exp": token_issued_at + ttl,
        "_user": {
            "username": user.username
        }
    }

    # Generate token.
    token = jwt.encode(token_payload, secret, algorithm=JWT_ALGORITHM)

    return token


def decode(token: str, secret: str) -> tuple[bool, bool, str]:
    """ Returns is given token valid and its payload. """
    token_payload = jwt.decode(token, secret, algorithms=JWT_ALGORITHM)
    return token_payload