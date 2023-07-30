# pylint: disable=raise-missing-from
"""
    Service for email confirmation / verification.
"""

from app.services.tokens.exceptions import (
    TokenWrongTypeError,
    TokenInvalidSignatureError,
    TokenInvalidError,
    TokenExpiredError,
)
from app.services.tokens import EmailToken
from app.services.api import ApiErrorException, ApiErrorCode
from app.config import get_settings

# TODO: Allow specify URL for email confirmation.


def decode_email_token(token: str) -> EmailToken:
    """
    Decodes email token and returns it, or raises API error if failed to decode.
    """
    try:
        email_token = EmailToken.decode(
            token, key=get_settings().security_email_tokens_secret_key
        )
    except (TokenInvalidError, TokenInvalidSignatureError):
        raise ApiErrorException(
            ApiErrorCode.EMAIL_CONFIRMATION_TOKEN_INVALID,
            "Confirmation token not valid, mostly due to corrupted link. Try resend confirmation again.",
        )
    except TokenExpiredError:
        raise ApiErrorException(
            ApiErrorCode.EMAIL_CONFIRMATION_TOKEN_INVALID,
            "Confirmation token expired. Try resend confirmation again.",
        )
    except TokenWrongTypeError:
        raise ApiErrorException(
            ApiErrorCode.EMAIL_CONFIRMATION_TOKEN_INVALID,
            "Expected token to be a confirmation token, not another type of token.",
        )
    return email_token


def generate_confirmation_link(user_id: int) -> str:
    """
    Encodes email token and returns confirmation link ready to be send to user email.
    """
    # TBD: Refactor this.
    settings = get_settings()

    # CFT string.
    confirmation_token = EmailToken(
        settings.security_tokens_issuer, settings.security_email_tokens_ttl, user_id
    ).encode(key=settings.security_email_tokens_secret_key)

    # confirmation_link = urllib.parse.urljoin(
    #    settings.proxy_url_domain,
    #    settings.proxy_url_prefix + "/_emailConfirmation.confirm",
    # )

    confirmation_endpoint = "https://florgon.com/email/verify"
    return f"{confirmation_endpoint}?cft={confirmation_token}"
