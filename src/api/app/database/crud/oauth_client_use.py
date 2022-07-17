"""
    OAuth client use CRUD utils for the database.
"""

# Libraries.
from sqlalchemy.orm import Session

# Models.
from app.database.models.oauth_client_use import OAauthClientUse


def create(db: Session, user_id: int, client_id: int) -> OAauthClientUse:
    oauth_client_use = OAauthClientUse(user_id=user_id, client_id=client_id)
    db.add(oauth_client_use)
    db.commit()
    db.refresh(oauth_client_use)
    return oauth_client_use
