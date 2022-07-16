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
    """Returns generated token secret."""
    return secrets.token_urlsafe(32)


def get_by_id(db: Session, session_id: int) -> UserSession | None:
    """Returns session by it`s ID."""
    return db.query(UserSession).filter(UserSession.id == session_id).first()


def get_by_owner_id(db: Session, owner_id: int) -> list[UserSession]:
    return db.query(UserSession).filter(UserSession.owner_id == owner_id).all()


def get_by_ip_address_and_user_agent(
    db: Session, ip_address: str, user_agent: UserAgent
) -> UserSession | None:
    return (
        db.query(UserSession)
        .filter(UserSession.ip_address == ip_address)
        .filter(UserSession.user_agent_id == user_agent.id)
        .filter(UserSession.is_active is True)
        .first()
    )


def get_count(
    db: Session
) -> int:
    return db.query(UserSession).all().count()


def get_active_count(
    db: Session
) -> int:
    return db.query(UserSession).filter(UserSession.is_active == True).count()


def get_active_count_grouped(
    db: Session
) -> int:
    return db.query(UserSession).filter(UserSession.is_active == True).group_by(UserSession.owner_id).count()


def get_inactive_count(
    db: Session
) -> int:
    return db.query(UserSession).filter(UserSession.is_active == False).count()


def get_inactive_count_grouped(
    db: Session
) -> int:
    return db.query(UserSession).filter(UserSession.is_active == False).group_by(UserSession.owner_id).count()


def get_last(db: Session) -> UserSession:
    return db.query(UserSession).order_by(UserSession.time_created.desc()).limit(1).first()


def get_or_create_new(
    db: Session, owner_id: int, client_host: str, client_user_agent: str
) -> UserSession:
    """Returns user session or creates a new one."""

    # Query user agent.
    user_agent: UserAgent = crud.user_agent.get_or_create_by_string(
        db, client_user_agent
    )
    user_agent_id = user_agent.id

    queried_session: UserSession = get_by_ip_address_and_user_agent(
        db, client_host, user_agent
    )
    if queried_session and queried_session.owner_id == owner_id:
        return queried_session

    # Create new user session.
    session_token_secret = generate_secret()
    session = UserSession(
        owner_id=owner_id,
        token_secret=session_token_secret,
        ip_address=client_host,
        user_agent_id=user_agent_id,
    )

    # Apply user session in database.
    db.add(session)
    db.commit()
    db.refresh(session)

    return session
