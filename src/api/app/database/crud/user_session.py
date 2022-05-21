"""
    User session CRUD utils for the database.
"""

# Libraries.
import secrets
from sqlalchemy.orm import Session

# Services.
from app.database.models.user_session import UserSession


def generate_secret() -> str:
    """ Returns generated token secret. """
    return secrets.token_urlsafe(32)


def get_by_id(db: Session, session_id: int) -> UserSession:
    """ Returns session by it`s ID. """
    return db.query(UserSession).filter(UserSession.id == session_id).first()


def get_by_owner_id(db: Session, owner_id: int) -> list[UserSession]:
    return db.query(UserSession).filter(UserSession.owner_id == owner_id).all()

def create(db: Session, owner_id: int) -> UserSession:
    """Creates user session"""

    # Create new user session.
    session_token_secret = generate_secret()
    session = UserSession(owner_id=owner_id, token_secret=session_token_secret)

    # Apply user session in database.
    db.add(session)
    db.commit()
    db.refresh(session)

    return session