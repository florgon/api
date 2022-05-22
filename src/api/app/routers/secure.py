"""
    Authentication session API router.
    Provides API methods (routes) for working with session (Signin, signup).
    For external authorization (obtaining `access_token`, not `session_token`) see OAuth.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from api.app.services.api.errors import ApiErrorException

from app.services.request import query_auth_data_from_token, Request
from app.services.validators.user import validate_signup_fields
from app.services.passwords import check_password
from app.services.tokens import encode_session_jwt_token
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error, api_success
from app.services.serializers.user import serialize_user

from app.database.dependencies import get_db, Session
from app.database import crud
from app.config import get_settings, Settings


router = APIRouter()


@router.get("/secure.checkToken")
async def method_secure_check_token(req: Request, \
    token: str, \
    db: Session = Depends(get_db)) -> JSONResponse:
    """ Returns access token information. """

    return api_error(ApiErrorCode.API_NOT_IMPLEMENTED, "Not implemented yet")