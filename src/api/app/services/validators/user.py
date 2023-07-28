"""
    User validators.
"""
import re

from validate_email import validate_email
from app.services.passwords import check_password
from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.schemas.session import SignupModel
from app.database.models.user import User
from app.database.dependencies import Session
from app.database import crud
from app.config import get_settings, Settings

_MAPPED_EMAIL_DOMAINS_STANDARDIZED = {
    "yandex.ru": "ya.ru",
    "yandex.com": "ya.ru",
    "yandex.ua": "ya.ru",
    "yandex.by": "ya.ru",
    "yandex.kz": "ya.ru",
}


def normalize_phone_number(phone_number: str) -> str:
    """
    Remove all non-digits from phone_number.
    """
    return "".join([ch for ch in phone_number if ch.isdigit()])


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
        mail_host_user = ("".join(mail_host_user)).replace(".", "")  # type: ignore
        email = f"{mail_host_user}@{mail_host_domain}"

    if mail_host_domain in _MAPPED_EMAIL_DOMAINS_STANDARDIZED:
        # Something like `yandex.ru` is same as `ya.ru` (mail domains)
        standardized_email = email.split("@")
        standardized_email.pop()
        return "@".join(
            standardized_email + [_MAPPED_EMAIL_DOMAINS_STANDARDIZED[mail_host_domain]]
        )
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
    db: Session, username: str, check_is_taken: bool = True
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
    if len(username) >= 17:
        raise ApiErrorException(
            ApiErrorCode.AUTH_USERNAME_INVALID, "Username should be shorten than 17!"
        )
    settings = get_settings()
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


def validate_signup_fields(db: Session, model: SignupModel) -> None:
    """Validates that all fields passes signup base validation, or raises API error if not."""

    settings = get_settings()
    validate_username_field(db, model.username, check_is_taken=True)
    validate_password_field(model.password)
    validate_email_field(db, settings, model.email, check_is_taken=True)
    validate_phone_number_field(db, phone_number=model.phone_number)


def validate_signin_fields(user: User | None = None, password: str = "") -> User:
    """Validates that all fields passes signin base validation, or raises API error if not."""

    if not user or not check_password(
        password=password,
        hashed_password=user.password,  # type: ignore
        hash_method=user.security_hash_method,  # type: ignore
    ):
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_CREDENTIALS,
            "Invalid credentials for authentication.",
        )
    if not user.is_active:
        raise ApiErrorException(
            ApiErrorCode.USER_DEACTIVATED,
            "Unable to complete request as user was frozen (deactivated or blocked).",
        )

    return user


def validate_first_name_field(first_name: str) -> None:
    """
    Validates first_name, raises API error if name is invalid.
    """
    if not first_name and len(first_name) >= 21:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "First name should be longer than 0 and shorter than 21!",
        )


def validate_last_name_field(last_name: str) -> None:
    """
    Validates last_name, raises API error if name is invalid.
    """
    if not last_name or len(last_name) >= 21:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "Last name should be longer than 0 and shorter than 21!",
        )


def validate_profile_bio_field(bio: str) -> None:
    """
    Validates profile_bio, raises API error if bio is invalid.
    """
    if len(bio) >= 251:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "Profile bio should be shorter than 251!",
        )


def validate_profile_website_field(website: str) -> None:
    """
    Validates profile_website, raises API error if url is invalid.
    """
    if len(website) >= 251:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "Profile website should be shorter than 251!",
        )

    pattern = re.compile(
        r"^(https:\/\/|http:\/\/|)([\w_-]+\.){1,3}\w{1,10}(\/.*)?$",
        flags=re.U,
    )
    if not pattern.match(website):
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "Profile website should be shorter than 251!",
        )


def validate_phone_number_field(db: Session, phone_number: str) -> None:
    """
    Validates phone_number, then normailize it and validates normalized phone_number.
    Raises API error if phone_number is invalid.
    """
    if not phone_number:
        return

    if len(phone_number) <= 10 or len(phone_number) >= 31:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "Phone number should be longer than 10 and shorter than 31 or should be empty!",
        )
    phone_number = normalize_phone_number(phone_number)
    if len(phone_number) <= 10 or len(phone_number) >= 14:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "Phone number should contain more than 10 digits and less then 14 digits!",
        )

    if crud.user.phone_number_is_taken(db=db, phone_number=phone_number):
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST, "Phone number is already taken!"
        )


def validate_profile_social_username_field(social_username: str) -> None:
    """
    Validates github, vk, telegram usernames.
    """
    if not social_username:
        return

    if len(social_username) <= 3 or len(social_username) >= 51:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "Profile social username should be longer than 3 and"
            "shorter than 51 or should be empty!",
        )
