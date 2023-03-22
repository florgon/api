"""
    Check client request by session, and raises error if request is not valid for the session.
    (Session opened from another client).
"""

from sqlalchemy.orm import Session
from fastapi import Request
from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.database.models.user_session import UserSession
from app.database import crud
from app.config import get_settings

from api.app.services.request.get_from_request import get_client_host_from_request


def session_check_client_by_request(
    db: Session, session: UserSession, request: Request
) -> None:
    """
    Raises API exception if session does not pass internal auth system checks.
    """

    # If true, means that session detected as suspicious.
    is_suspicious = _check_session_is_suspicious(db, session, request)

    if is_suspicious:
        raise ApiErrorException(
            ApiErrorCode.AUTH_INVALID_TOKEN, "Session opened from another client!"
        )


def _check_session_is_suspicious(
    db: Session, session: UserSession, request: Request
) -> bool:
    """
    Returns true, if session is considered as suspicious.
    """
    settings = get_settings()

    # Setting, that means to reject only when there is both ip and user agent wrong.
    # If true, will reject when even one ip or user agent is wrong.
    reject_fast = not (
        settings.auth_reject_wrong_ip_addr and settings.auth_reject_wrong_user_agent
    )  # TODO. #not settings.auth_reject_wrong_only_both

    # Flags for wrong IP, user agent.
    is_wrong_ip = False
    is_wrong_ua = False

    # Client host (IP) is wrong.
    if settings.auth_reject_wrong_ip_addr:
        if get_client_host_from_request(request) != session.ip_address:
            is_wrong_ip = True
            if reject_fast:
                return True

    # Client user agent is wrong.
    if settings.auth_reject_wrong_user_agent:
        user_agent_string = request.headers.get("User-Agent")
        user_agent = crud.user_agent.get_by_string(db, user_agent_string)
        if user_agent is None or user_agent.id != session.user_agent_id:
            is_wrong_ua = True
            if reject_fast:
                return True

    # If we should fail when one of checks is wrong, and we do not triggered it,
    # Just return false as not triggered.
    if reject_fast:
        return False

    # Supposed to trigger when only both items are wrong.
    return is_wrong_ua and is_wrong_ip
