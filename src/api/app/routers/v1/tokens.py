"""
    Tokens API router.
    Provides methods for working with checking tokens and etc.
    Mostly used for server-side of services that works with the Florgon.
"""

from fastapi.responses import JSONResponse
from fastapi import Depends, APIRouter
from app.services.request.auth import (
    query_auth_data_from_token,
    parse_permissions_from_scope,
    AccessToken,
)
from app.services.api import api_success
from app.database.dependencies import Session

router = APIRouter(
    include_in_schema=True,
    tags=["tokens"],
    prefix="/tokens",
    default_response_class=JSONResponse,
)


@router.get("/check")
async def check_access_token(
    access_token: str,
    required_scope: str = "",
    db: Session = Depends(),
) -> JSONResponse:
    """
    Returns information about given token and requirements from the request.

    Notice: Currently, works only for access tokens and there is no requirements to extend that method.

    Can be used for external services that may request to check token from their end-users and request some permissions,
    the check will pass almost as internal decoding.
    """
    token: AccessToken = query_auth_data_from_token(  # type: ignore
        token=access_token,
        db=db,
        required_permissions=parse_permissions_from_scope(required_scope),
        allow_external_clients=True,
        request=None,
    ).token

    return api_success(
        {
            "scope": token.get_scope(),
            "user_id": token.get_subject(),
            "expires_at": token.get_expires_at(),
            "issued_at": token.get_issued_at(),
            "signature_is_valid": token.signature_is_valid(),
        }
    )
