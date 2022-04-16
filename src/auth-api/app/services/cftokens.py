"""
    Confirmation tokens utils.
"""

# Libraries.
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadData

def generate(payload: str, secret: str, salt: str) -> str:
    """ Returns token for payload based on given secret and salt. """
    serializer = URLSafeTimedSerializer(secret)
    token: str = serializer.dumps(payload, salt=salt)
    return token


def confirm(token: str, max_age: int, secret: str, salt: str) -> tuple[bool, str | None]:
    """ Returns token payload from token, if token is valid based on given secret and salt. """
    serializer = URLSafeTimedSerializer(secret)

    try:
        payload = serializer.loads(token, salt=salt, max_age=max_age)
    except BadData:
        return False, None

    return True, payload