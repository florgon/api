"""
    OAuth client CRUD utils for the database.
"""

# Libraries.
import secrets
from sqlalchemy.orm import Session

# Services.
from app.database.models.oauth_client import OAuthClient


def generate_secret() -> str:
    """Returns generate client secret."""
    return secrets.token_urlsafe(32)


def get_by_id(db: Session, client_id: int) -> OAuthClient:
    """Returns client by it`s ID."""
    return db.query(OAuthClient).filter(OAuthClient.id == client_id).first()


def get_by_owner_id(db: Session, owner_id: int) -> list[OAuthClient]:
    """Returns clients by it`s owner ID."""
    return db.query(OAuthClient).filter(OAuthClient.owner_id == owner_id).all()


def get_count_by_owner_id(db: Session, owner_id: int) -> list[OAuthClient]:
    """Returns count of clients by it`s owner ID."""
    return db.query(OAuthClient).filter(OAuthClient.owner_id == owner_id).count()


def expire(db: Session, client: OAuthClient):
    """Regenerates client secret."""
    client.secret = generate_secret()
    db.commit()


def create(db: Session, owner_id: int, display_name: str) -> OAuthClient:
    """Creates OAuth client"""

    # Create new OAuth client.
    oauth_client_secret = generate_secret()
    oauth_client = OAuthClient(
        secret=oauth_client_secret, owner_id=owner_id, display_name=display_name
    )

    # Apply OAuth client in database.
    db.add(oauth_client)
    db.commit()
    db.refresh(oauth_client)

    return oauth_client


def get_count(db: Session) -> int:
    return db.query(OAuthClient).all().count()


def get_active_count(db: Session) -> int:
    return db.query(OAuthClient).filter(OAuthClient.is_active == True).count()


def get_inactive_count(db: Session) -> int:
    return db.query(OAuthClient).filter(OAuthClient.is_active == False).count()


def get_last(db: Session) -> OAuthClient:
    return (
        db.query(OAuthClient).order_by(OAuthClient.time_created.desc()).limit(1).first()
    )
