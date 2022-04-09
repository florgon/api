"""
    Standartized API error cpdes container.
"""

from enum import Enum


class ApiErrorCode(Enum):
    """ API Standartized error codes. """

    # Auth field is taken.
    AUTH_USERNAME_TAKEN = 0, 400
    AUTH_EMAIL_TAKEN = 1, 400,

    # Other auth related.
    AUTH_INVALID_CREDENTIALS = 10, 400
    AUTH_REQUIRED = 20, 401

    # API.
    API_INVALID_REQUEST = 30, 400