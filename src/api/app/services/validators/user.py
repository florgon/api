"""
    User validators.
"""

from validate_email import validate_email


from app.config import get_settings, Settings
from app.database import crud
from app.services.api.errors import ApiErrorCode, ApiErrorException
from app.database.models.user import User
from app.services.passwords import check_password
from app.database.dependencies import Session

_MAPPED_EMAIL_DOMAINS_STANDARDIZED = {
    "yandex.ru": "ya.ru",
    "yandex.com": "ya.ru",
    "yandex.ua": "ya.ru",
    "yandex.by": "ya.ru",
    "yandex.kz": "ya.ru",
}


def convert_email_to_standardized(email: str) -> str:
    """
    Standartizes email by converting same ones.
    """

    # Emails are always lowercase (independant for case)
    email = email.lower()

    if "@" not in email:
        return email

    mail_host_domain = email.split("@")[-1]

    if mail_host_domain == "gmail.com" and "." in email:
        # `abc@gmail.com` is same as `a.b.c@gmail.com`
        mail_host_user = email.split("@")
        mail_host_user.pop()
        mail_host_user = ("".join(mail_host_user)).replace(".", "")
        email = f"{mail_host_user}@{mail_host_domain}"

    if mail_host_domain in _MAPPED_EMAIL_DOMAINS_STANDARDIZED:
        # Something like `yandex.ru` is same as `ya.ru` (mail domains)
        standardized_email = email.split("@")
        standardized_email.pop()
        standardized_email = "@".join(
            standardized_email + [_MAPPED_EMAIL_DOMAINS_STANDARDIZED[mail_host_domain]]
        )
        return standardized_email
    return email


def validate_password_field(password: str) -> None:
    """
    Raises API error if password not fullifies requirements.
    """
    # Check password.
    if len(password) <= 5:
        raise ApiErrorException(
            ApiErrorCode.AUTH_PASSWORD_INVALID, "Password should be longer than 5!"
        )
    if len(password) > 64:
        raise ApiErrorException(
            ApiErrorCode.AUTH_PASSWORD_INVALID, "Password should be shorten than 64!"
        )


def validate_email_field(
    db: Session, settings: Settings, email: str, check_is_taken: bool = True
) -> None:
    """
    Raises API error if email is invalid or taken.
    """
    # Validate email.
    if crud.user.email_is_taken(db=db, email=email):
        raise ApiErrorException(
            ApiErrorCode.AUTH_EMAIL_TAKEN, "Given email is already taken!"
        )

    if (
        check_is_taken
        and settings.signup_validate_email
        and not validate_email(email, verify=False)
    ):  # TODO.
        raise ApiErrorException(ApiErrorCode.AUTH_EMAIL_INVALID, "Email invalid!")


def validate_username_field(
    db: Session, settings: Settings, username: str, check_is_taken: bool = True
) -> None:
    """
    Raises API error if username is invalid or is taken.
    """
    # Check username is not taken.
    if check_is_taken and crud.user.username_is_taken(db=db, username=username):
        raise ApiErrorException(
            ApiErrorCode.AUTH_USERNAME_TAKEN, "Given username is already taken!"
        )
    # Check username.
    if len(username) <= 4:
        raise ApiErrorException(
            ApiErrorCode.AUTH_USERNAME_INVALID, "Username should be longer than 4!"
        )
    if len(username) > 16:
        raise ApiErrorException(
            ApiErrorCode.AUTH_USERNAME_INVALID, "Username should be shorten than 16!"
        )
    if settings.signup_username_reject_nonalpha and not username.isalpha():
        raise ApiErrorException(
            ApiErrorCode.AUTH_USERNAME_INVALID,
            "Username should only contain alphabet characters!",
        )
    if settings.signup_username_reject_uppercase and not username.islower():
        raise ApiErrorException(
            ApiErrorCode.AUTH_USERNAME_INVALID,
            "Username should only contain lowercase characters!",
        )


def validate_signup_fields(
    db: Session, username: str, email: str, password: str
) -> None:
    """Validates that all fields passes signup base validation, or raises API error if not."""

    settings = get_settings()
    validate_username_field(db, settings, username, check_is_taken=True)
    validate_password_field(password)
    validate_email_field(db, settings, email, check_is_taken=True)


def validate_signin_fields(user: User, password: str) -> None:
    """Validates that all fields passes signin base validation, or raises API error if not."""

    if not user or not check_password(
        password=password,
        hashed_password=user.password,
        hash_method=user.security_hash_method,
    ):
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "Invalid credentials for authentication.",
        )
