"""
    OAuth client use CRUD utils for the database.
"""

# Libraries.
from sqlalchemy.ext.asyncio import AsyncSession

# Models.
from app.database.models.oauth_client_use import OAauthClientUse


def create(db: AsyncSession, user_id: int, client_id: int) -> OAauthClientUse:
    oauth_client_use = OAauthClientUse(user_id=user_id, client_id=client_id)
    db.add(oauth_client_use)
    db.commit()
    db.refresh(oauth_client_use)
    return oauth_client_use


def get_unique_users(db: AsyncSession, client_id: int) -> int:
    return (
        db.query(OAauthClientUse.user_id)
        .filter(OAauthClientUse.client_id == client_id)
        .group_by(OAauthClientUse.user_id)
        .count()
    )


def get_uses(db: AsyncSession, client_id: int) -> int:
    return (
        db.query(OAauthClientUse).filter(OAauthClientUse.client_id == client_id).count()
    )
