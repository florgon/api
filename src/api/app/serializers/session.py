"""
    User session database model serializer.
"""


import time

from app.database.repositories import UserAgentsRepository
from app.database.models.user_session import UserSession
from app.database.dependencies import Session


def serialize(session: UserSession, db: Session, in_list: bool = False):
    """Returns dict object for API response with serialized session data."""

    user_agent = UserAgentsRepository(db).get_by_id(session.user_agent_id)
    user_agent_string = user_agent.user_agent
    serialized = {
        "id": session.id,
        "ip": session.ip_address,
        "geo_country": session.geo_country,
        "user_agent": user_agent_string,
        "created_at": time.mktime(session.time_created.timetuple()),
        "is_active": session.is_active,
    }

    return serialized if in_list else {"session": serialized}


def serialize_list(sessions: list[UserSession], db: Session) -> dict:
    """Returns dict object for API response with serialized sessions list data."""

    return {
        "sessions": [serialize(session, db=db, in_list=True) for session in sessions]
    }


serialize_sessions = serialize_list
serialize_session = serialize
