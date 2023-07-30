# pylint: disable=unused-argument
"""
    Resolves client credentials grant.
"""

from app.services.api import api_error, ApiErrorCode
from app.schemas.oauth import ResolveGrantModel
from app.database.dependencies import Session
from app.config import Settings


def oauth_client_credentials_grant(
    model: ResolveGrantModel, db: Session, settings: Settings
):
    """Resolves client credentials grant."""
    return api_error(
        ApiErrorCode.API_NOT_IMPLEMENTED,
        "Client credentials grant type is not implemented! (And will be not implemented soon).",
    )
