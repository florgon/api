"""
    User database model serializer.
"""

import time

def serialize(user):
    """Returns dict object for API response with serialized user data."""
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "time_created": time.mktime(user.time_created.timetuple()),
            "states": {
                "is_active": user.is_active,
                "is_confirmed": user.is_verified,
            }
        }
    }
