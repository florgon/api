"""
    Confirmation tokens utils.
"""

# Libraries.
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadData
import urllib.parse


def generate_cft(payload: str, secret: str, salt: str) -> str:
    """ Returns token for payload based on given secret and salt. """
    serializer = URLSafeTimedSerializer(secret)
    token: str = serializer.dumps(payload, salt=salt)
    return token


def confirm_cft(token: str, max_age: int, secret: str, salt: str) -> tuple[bool, str | None]:
    """ Returns token payload from token, if token is valid based on given secret and salt. """
    serializer = URLSafeTimedSerializer(secret)

    try:
        payload = serializer.loads(token, salt=salt, max_age=max_age)
    except BadData:
        return False, None

    return True, payload


def generate_confirmation_link(email: str, cft_secret: str, cft_salt: str, proxy_url_host: str, proxy_url_prefix: str) -> str:
    """ Returns confirmation link ready to be sent to user. """
    confirmation_token = generate_cft(email, cft_secret, cft_salt)
    confirmation_link = urllib.parse.urljoin(proxy_url_host, proxy_url_prefix + "/_emailConfirmation.confirm")
    return f"{confirmation_link}?cft={confirmation_token}"