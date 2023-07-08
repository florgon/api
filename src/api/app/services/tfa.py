"""
    Service to work with 2FA OTP.
"""

from pyotp import TOTP
from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.database.models.user import User
from app.config import get_settings


def validate_user_tfa_otp_from_request(tfa_otp: str, user: User):
    """
    Raises API error if user is required to send 2FA otp key.
    """
    if not user.security_tfa_enabled:
        return

    settings = get_settings()

    # Request 2FA OTP, raise error with continue information.
    if not tfa_otp:
        raise ApiErrorException(
            ApiErrorCode.AUTH_TFA_OTP_REQUIRED,
            "2FA authentication one time password required!",
            {"tfa_otp_required": True},
        )

    tfa_device = "email"  # Device type.

    # Get OTP generator.
    otp_secret_key = user.security_tfa_secret_key
    otp_interval = (
        settings.security_tfa_totp_interval_email
        if tfa_device == "email"
        else settings.security_tfa_totp_interval_mobile
    )
    totp = TOTP(s=otp_secret_key, interval=otp_interval)

    # If OTP is not valid, raise error.
    if not totp.verify(tfa_otp):
        raise ApiErrorException(
            ApiErrorCode.AUTH_TFA_OTP_INVALID,
            "2FA authentication one time password expired or invalid!",
        )


def generate_tfa_otp(user: User, device_type: str) -> str | None:
    """
    Generates TFA OTP (key) for given user.
    """
    if device_type != "email" or not user.security_tfa_enabled:
        return None

    # Get generator.
    settings = get_settings()
    return generate_tfa_otp_raw_email(
        secret_key=user.security_tfa_secret_key,
        interval=settings.security_tfa_totp_interval_email,
    )


def generate_tfa_otp_raw_email(
    secret_key: str, interval: int | None = None
) -> str | None:
    """
    Generates TFA OTP (key) for raw fields in email.
    """

    # Get generator.
    settings = get_settings()
    totp = TOTP(
        s=secret_key, interval=interval or settings.security_tfa_totp_interval_email
    )

    return totp.now()
