from fastapi import APIRouter, Depends

from app.services.permissions import parse_permissions_from_scope
from app.services.request import query_auth_data_from_token
from app.services.api.response import api_success, JSONResponse
from app.database.dependencies import get_db, Session


router = APIRouter()


@router.get("/secure.checkAccessToken")
async def method_secure_check_token(token: str, scope: str = "", \
    db: Session = Depends(get_db)) -> JSONResponse:
    """ Returns access token information. """
    required_permissions = parse_permissions_from_scope(scope)
    auth_data = query_auth_data_from_token(token, db, required_permissions=required_permissions)
    return api_success({
        "scope": auth_data.token_payload["scope"],
        "user_id": auth_data.token_payload["sub"],
        "expires_at": float(auth_data.token_payload.get("exp", 0)),
        "issued_at": auth_data.token_payload["iat"],
    })