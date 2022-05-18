"""
    User database model serializer.
"""

import time

def serialize(user, *, include_email: bool = False, include_optional_fields: bool = False):
    """Returns dict object for API response with serialized user data."""
    serialized_user = {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "sex": 0 if user.is_female() else 1
    }

    if include_email:
        serialized_user["email"] = user.email

    if include_optional_fields:
        serialized_user["time_created"] = time.mktime(user.time_created.timetuple())
        serialized_user["states"] = {
            "is_active": user.is_active,
            "is_confirmed": user.is_verified
        }

    
    return {
        "user": serialized_user
    }

serialize_user = serialize