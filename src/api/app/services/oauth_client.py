"""
    Service to work with oauth clients.
"""

from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.database.models.oauth_client import OAuthClient
from app.database.dependencies import Session
from app.database import crud


def query_oauth_client(
    db: Session, client_id: int, owner_id: int | None = None
) -> OAuthClient:
    """
    Returns oauth client by id or raises API error if not found or inactive.
    If given owner_id, returns only oauth clients owned by that user.
    """
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)
    if not oauth_client or not oauth_client.is_active:
        raise ApiErrorException(
            ApiErrorCode.OAUTH_CLIENT_NOT_FOUND,
            "OAuth client not found or deactivated!",
        )

    if owner_id is not None and oauth_client.owner_id != owner_id:
        raise ApiErrorException(
            ApiErrorCode.OAUTH_CLIENT_FORBIDDEN,
            "You are not owner of this OAuth client!",
        )
    return oauth_client
