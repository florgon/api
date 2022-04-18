"""
    User validators.
"""

# Libraries.
from validate_email import validate_email

# Database.
from app.database import crud

# Services.
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error


def validate_signup_fields(db, username, email, password):
    """Returns dict object for API response with serialized user data."""

    # Validate email.
    if crud.user.email_is_taken(db=db, email=email):
        return False, api_error(ApiErrorCode.AUTH_EMAIL_TAKEN, "Given email is already taken!")

    # Validate username.
    if crud.user.username_is_taken(db=db, username=username):
        return False, api_error(ApiErrorCode.AUTH_USERNAME_TAKEN, "Given username is already taken!")

    # Check email.
    if not validate_email(email, verify=False): # TODO.
        return False, api_error(ApiErrorCode.AUTH_EMAIL_INVALID, "Email invalid!")

    # Check username.
    if len(username) <= 4:
        return False, api_error(ApiErrorCode.AUTH_USERNAME_INVALID, "Username should be longer than 4!")
    if len(username) > 16:
        return False, api_error(ApiErrorCode.AUTH_USERNAME_INVALID, "Username should be shorten than 16!")
    if not username.isalpha() or not username.islower():
        return False, api_error(ApiErrorCode.AUTH_USERNAME_INVALID, "Username should only contain lowercase alphabet characters!")
    
    # Check password.
    if len(password) <= 5:
        return False, api_error(ApiErrorCode.AUTH_PASSWORD_INVALID, "Password should be longer than 5!")
    if len(password) > 64:
        return False, api_error(ApiErrorCode.AUTH_PASSWORD_INVALID, "Password should be shorten than 64!")

    # All ok.
    return True, None