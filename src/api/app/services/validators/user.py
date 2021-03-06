"""
    User validators.
"""

# Libraries.
from validate_email import validate_email

# Database.
from app.database import crud

# Services.
from app.services.api.errors import ApiErrorCode, ApiErrorException


def validate_signup_fields(db, username, email, password):
    """Returns dict object for API response with serialized user data."""

    # Check email is not taken.
    if crud.user.email_is_taken(db=db, email=email):
        raise ApiErrorException(
            ApiErrorCode.AUTH_EMAIL_TAKEN, "Given email is already taken!"
        )

    # Validate username.
    if crud.user.username_is_taken(db=db, username=username):
        raise ApiErrorException(
            ApiErrorCode.AUTH_USERNAME_TAKEN, "Given username is already taken!"
        )

    # Validate email.
    if not validate_email(email, verify=False):  # TODO.
        raise ApiErrorException(ApiErrorCode.AUTH_EMAIL_INVALID, "Email invalid!")

    # Check username.
    if len(username) <= 4:
        raise ApiErrorException(
            ApiErrorCode.AUTH_USERNAME_INVALID, "Username should be longer than 4!"
        )
    if len(username) > 16:
        raise ApiErrorException(
            ApiErrorCode.AUTH_USERNAME_INVALID, "Username should be shorten than 16!"
        )
    if not username.isalpha() or not username.islower():
        raise ApiErrorException(
            ApiErrorCode.AUTH_USERNAME_INVALID,
            "Username should only contain lowercase alphabet characters!",
        )

    # Check password.
    if len(password) <= 5:
        raise ApiErrorException(
            ApiErrorCode.AUTH_PASSWORD_INVALID, "Password should be longer than 5!"
        )
    if len(password) > 64:
        raise ApiErrorException(
            ApiErrorCode.AUTH_PASSWORD_INVALID, "Password should be shorten than 64!"
        )
