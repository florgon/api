"""
    Stuff for working with sessions.
"""

from fastapi import Request
from app.tokens import SessionToken
from app.services.request import get_country_from_request, get_client_host_from_request
from app.database.models.user_session import UserSession
from app.database.models.user import User
from app.database.dependencies import Session
from app.database import crud
from app.config import get_settings


def publish_new_session_with_token(
    user: User,
    user_agent: str,
    db: Session,
    req: Request,
) -> tuple[SessionToken, UserSession]:
    """
    Returns new published session with token for given user with passed all required stuff.
    """
    settings = get_settings()
    session = _publish_new_session(user.id, req, db, user_agent)
    token = SessionToken(
        settings.security_tokens_issuer,
        settings.security_session_tokens_ttl,
        user.id,
        session.id,
    )
    return token, session


def _publish_new_session(owner_id: int, req: Request, db: Session, user_agent: str):
    """
    Publishes new session and returns it.
    """
    session_user_agent = user_agent
    session_client_host = get_client_host_from_request(req)
    session_geo_country = get_country_from_request(req)
    session = crud.user_session.get_or_create_new(
        db, owner_id, session_client_host, session_user_agent, session_geo_country
    )
    return session
