"""
    User session database model serializer.
"""


import time

from app.database.dependencies import Session
from app.database.models.user_session import UserSession
from app.database.crud.user_agent import get_by_id as get_user_agent_by_id


def serialize(session: UserSession, db: Session, in_list: bool = False):
    """Returns dict object for API response with serialized session data."""

    serialized_session = {
        "id": session.id,
        "ip": session.ip_address,
        "user_agent": get_user_agent_by_id(
            db=db, user_agent_id=session.user_agent_id
        ).user_agent,
        "created_at": time.mktime(session.time_created.timetuple()),
    }

    if in_list:
        return serialized_session

    return {"session": serialized_session}


def serialize_list(
    sessions: list[UserSession], db: Session, *, include_deactivated: bool = False
) -> dict:
    """Returns dict object for API response with serialized sessions list data."""

    return {
        "sessions": [
            serialize(session, db=db, in_list=True)
            for session in sessions
            if (session.is_active or include_deactivated)
        ]
    }


serialize_sessions = serialize_list
serialize_session = serialize
