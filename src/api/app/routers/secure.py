"""
    Secure API router.
    Provides API methods (routes) for working with server-side with client apps servers.
"""
from app.database.dependencies import Session, get_db
from app.services.api.response import JSONResponse, api_success
from app.services.permissions import parse_permissions_from_scope
from app.services.request import query_auth_data_from_token
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/secure.checkAccessToken")
async def method_secure_check_token(
    token: str, scope: str = "", db: Session = Depends(get_db)
) -> JSONResponse:
    """Returns access token information."""
    required_permissions = parse_permissions_from_scope(scope)
    auth_data = query_auth_data_from_token(
        token, db, required_permissions=required_permissions
    )
    return api_success(
        {
            "scope": auth_data.token.get_scope(),
            "user_id": auth_data.token.get_subject(),
            "expires_at": auth_data.token.get_expires_at(),
            "issued_at": auth_data.token.get_issued_at(),
        }
    )
