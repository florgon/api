# pylint: disable=singleton-comparison
"""
    OAuth client use CRUD utils for the database.
"""

from app.database.models.oauth_client_use import OAuthClientUse
from sqlalchemy.orm import Session


def create(db: Session, user_id: int, client_id: int) -> OAuthClientUse:
    """Creates new OAuth client use object that is committed in the database already."""
    oauth_client_use = OAuthClientUse(user_id=user_id, client_id=client_id)
    db.add(oauth_client_use)
    db.commit()
    db.refresh(oauth_client_use)
    return oauth_client_use


def get_unique_users(db: Session, client_id: int) -> int:
    """Returns count of all uses of oauth client by different users."""
    return (
        db.query(OAuthClientUse.user_id)
        .filter(OAuthClientUse.client_id == client_id)
        .group_by(OAuthClientUse.user_id)
        .count()
    )


def get_uses(db: Session, client_id: int) -> int:
    """Returns count of all uses of oauth client."""
    return (
        db.query(OAuthClientUse).filter(OAuthClientUse.client_id == client_id).count()
    )
