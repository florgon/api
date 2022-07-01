"""
    User database model serializer.
"""

import time


def serialize(
    user,
    *,
    include_email: bool = False,
    include_optional_fields: bool = False,
    include_private_fields: bool = False,
    include_profile_fields: bool = False
):
    """Returns dict object for API response with serialized user data."""
    serialized_user = {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "sex": 0 if user.is_female() else 1,
    }

    if include_profile_fields:
        serialized_user["profile"] = {
            "bio": user.profile_bio,
            "website": user.profile_website,
            "socials": {
                "vk": user.profile_social_username_vk,
                "tg": user.profile_social_username_tg,
                "gh": user.profile_social_username_gh,
            },
        }

    if include_email and include_private_fields:
        serialized_user["email"] = user.email

    if include_optional_fields:
        serialized_user["time_created"] = time.mktime(user.time_created.timetuple())
        serialized_user["states"] = {
            "is_active": user.is_active,
        }
        if include_private_fields:
            serialized_user["states"]["is_confirmed"] = user.is_verified

    return {"user": serialized_user}


serialize_user = serialize
