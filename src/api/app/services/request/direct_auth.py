"""
    Request checker for direct auth process.
"""

from fastapi import Request
from app.services.api.errors import ApiErrorException, ApiErrorCode


def check_direct_auth_is_allowed(request: Request) -> None:
    """
    Raises API error if direct auth is not allowed for request.
    Checks that request is coming from an authorized application, not from default user.
    Used for dissalowing direct auth (signup/login) for everyone except web domains.
    For auth process there is OAuth workflow.

    TODO: Better check for direct auth.
    TODO: Logging.
    TODO: Configuration.
    """
    direct_auth_host = request.headers.get("florgon-direct-auth-host", None)
    if direct_auth_host is None or direct_auth_host != "florgon-web":
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN, "Direct auth is not allowed for you!"
        )
