from fastapi import Request
from fastapi.responses import JSONResponse

# Grants.
from .grant_types.authorization_code import oauth_authorization_code_grant
from .grant_types.refresh_token import oauth_refresh_token_grant
from .grant_types.password import oauth_password_grant
from .grant_types.client_credentials import oauth_client_credentials_grant

# App.
from app.config import Settings
from app.database.dependencies import Session
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error


def resolve_grant(
    grant_type: str,
    req: Request,
    client_id: int,
    client_secret: str,
    db: Session,
    settings: Settings,
) -> JSONResponse:
    """"""
    if not grant_type or grant_type == "authorization_code":
        return oauth_authorization_code_grant(
            req, client_id, client_secret, db, settings
        )

    if grant_type == "refresh_token":
        return oauth_refresh_token_grant(req, client_id, client_secret, db, settings)

    if grant_type == "password":
        return oauth_password_grant(req, client_id, client_secret, db, settings)

    if grant_type == "client_credentials":
        return oauth_client_credentials_grant(
            req, client_id, client_secret, db, settings
        )

    # Requested grant_type is not exists.
    return api_error(
        ApiErrorCode.API_INVALID_REQUEST,
        "Unknown `grant_type` value! "
        "Allowed: `authorization_code`, `password`, `client_credentials`, `refresh_token`.",
    )
