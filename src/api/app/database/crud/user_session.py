"""
    User session CRUD utils for the database.
"""

# Libraries.
import secrets
from sqlalchemy.orm import Session

# CRUD.
from app.database import crud
# Models.
from app.database.models.user_session import UserSession
from app.database.models.user_agent import UserAgent


def generate_secret() -> str:
    """ Returns generated token secret. """
    return secrets.token_urlsafe(32)


def get_by_id(db: Session, session_id: int) -> UserSession:
    """ Returns session by it`s ID. """
    return db.query(UserSession).filter(UserSession.id == session_id).first()


def get_by_owner_id(db: Session, owner_id: int) -> list[UserSession]:
    return db.query(UserSession).filter(UserSession.owner_id == owner_id).all()

def create(db: Session, owner_id: int, client_host: str, client_user_agent: str) -> UserSession:
    """Creates user session"""

    # Query user agent.
    user_agent: UserAgent = crud.user_agent.get_or_create_by_string(db, client_user_agent)
    user_agent_id = user_agent.id

    # Create new user session.
    session_token_secret = generate_secret()
    session = UserSession(
        owner_id=owner_id, 
        token_secret=session_token_secret, 
        ip_address=client_host,
        user_agent_id=user_agent_id)

    # Apply user session in database.
    db.add(session)
    db.commit()
    db.refresh(session)

    return session