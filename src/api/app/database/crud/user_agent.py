"""
    User agent CRUD utils for the database.
"""

# Libraries.
from sqlalchemy.orm import Session

# Models.
from app.database.models.user_agent import UserAgent


def get_by_string(db: Session, user_agent_string: str) -> UserAgent:
    """Returns user agent by it`s string."""
    user_agent = (
        db.query(UserAgent).filter(UserAgent.user_agent == user_agent_string).first()
    )
    return user_agent


def get_by_id(db: Session, user_agent_id: int) -> UserAgent | None:
    """Returns user agent by it`s id."""
    return db.query(UserAgent).filter(UserAgent.id == user_agent_id).first()


def get_or_create_by_string(db: Session, user_agent_string: str) -> UserAgent:
    """Creates or returns already created user agent."""
    user_agent = get_by_string(db, user_agent_string)
    if user_agent is None:
        user_agent = UserAgent(user_agent=user_agent_string)
        db.add(user_agent)
        db.commit()
        db.refresh(user_agent)
    return user_agent
