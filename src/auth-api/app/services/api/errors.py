"""
    Standartized API error cpdes container.
"""

from enum import Enum


class ApiErrorCode(Enum):
    """ API Standartized error codes. """

    # Auth field is taken.
    AUTH_USERNAME_TAKEN = 0, 400
    AUTH_EMAIL_TAKEN = 1, 400,

    # Auth token.
    AUTH_INVALID_TOKEN = 10, 400
    AUTH_EXPIRED_TOKEN = 11, 400

    # Other auth related.
    AUTH_INVALID_CREDENTIALS = 20, 400
    AUTH_REQUIRED = 21, 401
    AUTH_EMAIL_INVALID = 30, 400
    AUTH_PASSWORD_INVALID = 31, 400
    AUTH_USERNAME_INVALID = 32, 400

    # API.
    API_INVALID_REQUEST = 40, 400