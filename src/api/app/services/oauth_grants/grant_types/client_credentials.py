# pylint: disable=unused-argument
"""
    Resolves client credentials grant.
"""

from app.config import Settings
from app.database.dependencies import Session
from app.services.api.errors import ApiErrorCode
from app.services.api.response import api_error
from fastapi import Request


def oauth_client_credentials_grant(
    req: Request, client_id: int, client_secret: str, db: Session, settings: Settings
):
    """Resolves client credentials grant."""
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Client credentials grant type is not implemented! (And will be not implemented soon).",
    )
