"""
    Stuff for working with sessions.
"""

from fastapi import Request
from app.services.tokens import SessionToken
from app.services.request import (
    get_user_agent_from_request,
    get_country_from_request,
    get_client_host_from_request,
)
from app.database.models.user import User
from app.database.dependencies import Session
from app.database import crud
from app.config import get_settings


def publish_new_session_with_token(
    user: User,
    db: Session,
    req: Request,
) -> tuple[str, int]:
    """
    Returns new published session (ID of it) with token (already encoded) for given user with passed all required stuff.
    """
    owner_id: int = user.id  # type: ignore
    session = _publish_new_session_or_get_old(owner_id, req, db)
    token = _publish_new_token(session.id, owner_id).encode(key=session.token_secret)
    return token, session.id


def _publish_new_session_or_get_old(owner_id: int, req: Request, db: Session):
    """
    Publishes new session and returns it.
    """
    return crud.user_session.get_or_create_new(
        db,
        owner_id,
        client_host=get_client_host_from_request(req),
        client_user_agent=get_user_agent_from_request(req),
        client_geo_country=get_country_from_request(req),
    )


def _publish_new_token(session_id: int, owner_id: int) -> SessionToken:
    """
    Returns fresh new session token for session with owner u serid.
    """
    settings = get_settings()
    return SessionToken(
        settings.security_tokens_issuer,
        settings.security_session_tokens_ttl,
        owner_id,
        session_id,
    )
