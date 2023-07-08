# pylint: disable=singleton-comparison
"""
    OAuth client user CRUD utils for the database.
"""

from sqlalchemy.orm import Session
from app.database.models.oauth_client_user import OAuthClientUser


def create_if_not_exists(
    db: Session, user_id: int, client_id: int, scope: str
) -> OAuthClientUser:
    """Creates new OAuth client user object that is committed in the database already if not found."""

    oauth_client_user = (
        db.query(OAuthClientUser)
        .filter(OAuthClientUser.client_id == client_id)
        .filter(OAuthClientUser.user_id == user_id)
        .first()
    )

    if not oauth_client_user:
        oauth_client_user = OAuthClientUser(
            user_id=user_id, client_id=client_id, requested_scope=scope
        )
        db.add(oauth_client_user)
        db.commit()
        db.refresh(oauth_client_user)

    if not oauth_client_user.is_active or oauth_client_user.requested_scope != scope:
        oauth_client_user.requested_scope = scope
        oauth_client_user.is_active = True
        db.add(oauth_client_user)
        db.commit()

    return oauth_client_user


def get_by_user_id(db: Session, user_id: int) -> list[OAuthClientUser]:
    """Returns all oauth client users by user ID."""
    return (
        db.query(OAuthClientUser)
        .filter(OAuthClientUser.is_active == True)
        .filter(OAuthClientUser.user_id == user_id)
        .all()
    )


def get_by_client_and_user_id(
    db: Session, user_id: int, client_id: int
) -> OAuthClientUser | None:
    """Returns oauth client user by user and client ID."""
    return (
        db.query(OAuthClientUser)
        .filter(OAuthClientUser.is_active == True)
        .filter(OAuthClientUser.user_id == user_id)
        .filter(OAuthClientUser.client_id == client_id)
        .first()
    )
