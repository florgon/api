"""
    Secure API router.
    Provides API methods (routes) for working with server-side with client apps servers.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success
from app.services.request.auth import (
    AuthDataFromTokenWithScopeDependency,
    AuthData,
)


router = APIRouter()


@router.route("/secure.checkAccessToken", methods=["GET"])
async def method_secure_check_access_token(
    auth_data: AuthData = Depends(
        AuthDataFromTokenWithScopeDependency(
            only_session_token=False,
            allow_external_clients=True,
            trigger_online_update=True,
        )
    ),
) -> JSONResponse:
    """
    Returns information about access (only) token.
    Can be used for external services that may request to check token from their end-users and request some permissions,
    the check will pass almost as internal decoding.
    """

    # Information that is NOT shown to the end-user:
    # - Session ID.

    return api_success(
        {
            "scope": auth_data.token.get_scope(),
            "user_id": auth_data.token.get_subject(),
            "expires_at": auth_data.token.get_expires_at(),
            "issued_at": auth_data.token.get_issued_at(),
            "signature_is_valid": auth_data.token.signature_is_valid(),
        }
    )


@router.route("/secure.checkRefreshToken", methods=["GET"])
async def method_secure_check_refresh_token() -> JSONResponse:
    """
    Returns information about refresh (only) token.
    """

    return api_error(
        ApiErrorCode.API_FORBIDDEN, "You are not allowed to check refresh tokens!"
    )


@router.route("/secure.checkSessionToken", methods=["GET"])
async def method_secure_check_session_token() -> JSONResponse:
    """
    Returns information about session (only) token.
    """
    return api_error(
        ApiErrorCode.API_FORBIDDEN, "You are not allowed to check session tokens!"
    )
