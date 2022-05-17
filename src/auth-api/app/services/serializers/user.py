"""
    User database model serializer.
"""

import time

def serialize(user, *, include_email: bool = False, include_optional_fields: bool = False):
    """Returns dict object for API response with serialized user data."""
    serialized_user = {
        "id": user.id,
        "username": user.username,
    }

    if include_email:
        serialized_user["email"] = user.email

    if include_optional_fields:
        serialized_user["states"] = time.mktime(user.time_created.timetuple())
        serialized_user["time_created"] = {
            "is_active": user.is_active,
            "is_confirmed": user.is_verified
        }
    
    return {
        "user": serialized_user
    }

serialize_user = serialize