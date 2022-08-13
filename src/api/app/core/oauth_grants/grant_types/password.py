# pylint: disable=unused-argument
"""
    Resolves password grant.
"""

from app.core.config import Settings
from app.core.database.dependencies import Session
from app.core.services.api.errors import ApiErrorCode
from app.core.services.api.response import api_error

from fastapi import Request


def oauth_password_grant(
    req: Request, client_id: int, client_secret: str, db: Session, settings: Settings
):
    """Resolves password grant."""
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Password grant type is not implemented! (And will be not implemented soon).",
    )
