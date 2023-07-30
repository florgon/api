# pylint: disable=unused-argument
"""
    Resolves password grant.
"""

from app.services.api import api_error, ApiErrorCode
from app.schemas.oauth import ResolveGrantModel
from app.database.dependencies import Session
from app.config import Settings


def oauth_password_grant(model: ResolveGrantModel, db: Session, settings: Settings):
    """Resolves password grant."""
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Password grant type is not implemented! (And will be not implemented soon).",
    )
