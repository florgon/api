"""
    Check that host (client) request for signup allowance, and raises error if request is not valid for the signup.
    (Like server considered signup request as multiaccounts user (or user is bypassing restrictions imposed on it)).
"""

from sqlalchemy.orm import Session
from fastapi import Request
from app.services.request.get_from_request import get_client_host_from_request
from app.services.api import ApiErrorException, ApiErrorCode
from app.database.repositories import UserSessionsRepository
from app.config import get_settings


def validate_signup_host_allowance(db: Session, request: Request) -> None:
    """
    Raises API exception if signup host (client) does not pass internal auth system checks for fraud / etc (is blocked).
    """

    settings = get_settings()

    client_host = get_client_host_from_request(request=request)
    sessions = UserSessionsRepository(db).get_by_ip_address(client_host)

    if not settings.signup_multiaccounting_dissalowed:
        return

    reject_request = False
    if not settings.signup_multiaccounting_only_for_non_bypass:
        if len(sessions) != 0:
            reject_request = True
    else:
        # Currently there is no logic to handle that.
        # TODO: Block multiaccounting for bypass only.
        if len(sessions) != 0:
            reject_request = True

    if reject_request:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN,
            "Detected multiaccounting request! Please contact support if you get this by an accident.",
        )
