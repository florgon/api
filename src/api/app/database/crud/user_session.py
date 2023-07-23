# pylint: disable=singleton-comparison
"""
    User session CRUD utils for the database.
"""


import secrets

from sqlalchemy.orm import Session
from app.database.models.user_session import UserSession
from app.database.models.user_agent import UserAgent
from app.database.crud.user_agent import (
    get_or_create_by_string as get_ua_or_crete_by_string,
)


def generate_secret() -> str:
    """Returns generated token secret."""
    return secrets.token_urlsafe(32)


def get_by_id(db: Session, session_id: int) -> UserSession | None:
    """Returns session by it`s ID."""
    return db.query(UserSession).filter(UserSession.id == session_id).first()


def get_all_by_owner_id(db: Session, owner_id: int) -> list[UserSession]:
    """Returns list of sessions by owner user id."""
    return db.query(UserSession).filter(UserSession.owner_id == owner_id).all()


def get_active_by_owner_id(db: Session, owner_id: int) -> list[UserSession]:
    """Returns list of sessions by owner user id."""
    return (
        db.query(UserSession)
        .filter(UserSession.owner_id == owner_id)
        .filter(UserSession.is_active == True)
        .all()
    )


def deactivate_list(db, sessions: list[UserSession]) -> None:
    """Deactivates list of a sessions."""
    for session in sessions:
        session.is_active = False  # type: ignore
    db.commit()


def deactivate_one(db, session: UserSession) -> None:
    """Deactivates one session."""
    session.is_active = False  # type: ignore
    db.commit()


def get_by_ip_address_and_user_agent(
    db: Session, ip_address: str, user_agent: UserAgent
) -> UserSession | None:
    """Returns session by ip address and user agent."""
    return (
        db.query(UserSession)
        .filter(UserSession.ip_address == ip_address)
        .filter(UserSession.user_agent_id == user_agent.id)
        .filter(UserSession.is_active == True)
        .first()
    )


def get_by_ip_address(
    db: Session, ip_address: str, active_only: bool = False, limit: int = -1
) -> list[UserSession]:
    """Returns session by ip address."""
    query = db.query(UserSession).filter(UserSession.ip_address == ip_address)
    if active_only:
        query.filter(UserSession.is_active == True)
    if limit >= 1:
        query.limit(limit)
    return query.all()


def get_count(db: Session) -> int:
    """Returns total count of session in the database."""
    return db.query(UserSession).count()


def get_active_count(db: Session) -> int:
    """Returns total active session count in the database."""
    return db.query(UserSession).filter(UserSession.is_active == True).count()


def get_active_count_grouped(db: Session) -> int:
    """Returns active session count grouped by users."""
    return (
        db.query(UserSession.owner_id)
        .filter(UserSession.is_active == True)
        .group_by(UserSession.owner_id)
        .count()
    )


def get_inactive_count(db: Session) -> int:
    """Returns total inactive session count in the database."""
    return db.query(UserSession).filter(UserSession.is_active == False).count()


def get_inactive_count_grouped(db: Session) -> int:
    """Returns inactive session count grouped by users."""
    return (
        db.query(UserSession.owner_id)
        .filter(UserSession.is_active == False)
        .group_by(UserSession.owner_id)
        .count()
    )


def get_last(db: Session) -> UserSession | None:
    """Returns last created session."""
    return (
        db.query(UserSession).order_by(UserSession.time_created.desc()).limit(1).first()
    )


def get_or_create_new(
    db: Session,
    owner_id: int,
    client_host: str,
    client_user_agent: str,
    client_geo_country: str | None = None,
) -> UserSession:
    """Returns user session or creates a new one."""

    # Query user agent.
    user_agent: UserAgent = get_ua_or_crete_by_string(db, client_user_agent)
    user_agent_id = user_agent.id

    queried_session = get_by_ip_address_and_user_agent(db, client_host, user_agent)
    if queried_session and queried_session.owner_id == owner_id:
        return queried_session

    # Create new user session.
    session_token_secret = generate_secret()
    session = UserSession(
        owner_id=owner_id,
        token_secret=session_token_secret,
        ip_address=client_host,
        user_agent_id=user_agent_id,
        geo_country=client_geo_country or "",  # TODO: nullable.
    )

    # Apply user session in database.
    db.add(session)
    db.commit()
    db.refresh(session)

    return session
