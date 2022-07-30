"""
    User security API router.
    Provides API methods (routes) for working with user security.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.services.permissions import Permission
from app.services.request import query_auth_data_from_request
from app.services.api.response import api_error, api_success, ApiErrorCode

from app.database.dependencies import get_db, Session

router = APIRouter()


@router.get("/security.getInfo")
async def method_security_get_inof(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns secutity information about current user."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.security]
    )
    user = auth_data.user
    return api_success(
        {
            "security": {
                "tfa": {
                    "enabled": user.security_tfa_enabled,
                    "can_enabled": user.is_verified,
                    "device_type": "email",
                }
            }
        }
    )


@router.get("/security.userEnableTfa")
async def method_security_user_enable_tfa(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Enables TFA for the current user."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.security]
    )
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Security not implemented yet (2FA not implemented).",
    )


@router.get("/security.userDisableTfa")
async def method_security_user_disable_tfa(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Disables TFA for the current user."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.security]
    )
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Security not implemented yet (2FA not implemented).",
    )


@router.get("/security.userRequestChangePassword")
async def method_security_user_request_change_password(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Requests change password for the current user."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.security]
    )
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Security not implemented yet (Password change not implemented).",
    )


@router.get("/security.userAcceptChangePassword")
async def method_security_user_accept_change_password(
    req: Request, db: Session = Depends(get_db)
) -> JSONResponse:
    """Accepts change password for the current user."""
    auth_data = query_auth_data_from_request(
        req, db, required_permissions=[Permission.security]
    )
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Security not implemented yet (Password change not implemented).",
    )
