"""
    Resolves from grant_type string name grant type resolver.
"""

from fastapi.responses import JSONResponse
from app.services.api import ApiErrorException, ApiErrorCode
from app.schemas.oauth import ResolveGrantModel, GrantType
from app.database.dependencies import Session
from app.config import Settings

from .types.refresh_token import oauth_refresh_token_grant
from .types.password import oauth_password_grant
from .types.client_credentials import oauth_client_credentials_grant
from .types.authorization_code import oauth_authorization_code_grant

RESOLVERS = {
    GrantType.authorization_code: oauth_authorization_code_grant,
    GrantType.refresh_token: oauth_refresh_token_grant,
    GrantType.password: oauth_password_grant,
    GrantType.client_credentials: oauth_client_credentials_grant,
}


async def resolve_grant(
    model: ResolveGrantModel,
    db: Session,
    settings: Settings,
) -> JSONResponse:
    """
    Resolves string of the grant type to tokens (access, access+refresh pair).
    """
    if model.grant_type not in RESOLVERS:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "Unknown `grant_type` value! "
            "Allowed: `authorization_code`, `password`, `client_credentials`, `refresh_token`.",
        )
    return RESOLVERS[model.grant_type](model=model, db=db, settings=settings)
