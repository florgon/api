
def serialize(user):
    """Returns dict object for API response with serialized user data."""
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    }