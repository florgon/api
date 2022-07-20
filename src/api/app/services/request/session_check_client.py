"""
    Check client request by session, and raises error if request is not valid for the session.
    (Session opened from another client).
"""

from sqlalchemy.orm import Session
from fastapi import Request

from app.database import crud
from app.database.models.user_session import UserSession
from app.services.api.errors import ApiErrorCode, ApiErrorException
from app.services.request.get_client_host import get_client_host_from_request


def session_check_client_by_request(db: Session, session: UserSession, request: Request) -> None:
    """
    Raises API exception if session was opened from another client.
    """

    # Client host (IP) is wrong.
    if get_client_host_from_request(request) != session.ip_address:
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Session opened from another client!"
        )

    # Client user agent is wrong.
    user_agent_string = request.headers.get("User-Agent")
    user_agent = crud.user_agent.get_by_string(db, user_agent_string)
    if user_agent is None or user_agent.id != session.user_agent_id:
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Session opened from another client!"
        )