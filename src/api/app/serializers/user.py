"""
    User database model serializer.
"""


import time
from typing import Any

from app.database.models.user import User


def serialize(
    user: User,
    *,
    in_list: bool = False,
    include_email: bool = False,
    include_optional_fields: bool = False,
    include_private_fields: bool = False,
    include_profile_fields: bool = False,
    include_phone: bool = False,
) -> dict[str, Any]:
    """Returns dict object for API response with serialized user data."""
    serialized: dict[str, Any] = {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "sex": int(user.sex),
    }

    if include_profile_fields:
        serialized["profile"] = {
            "bio": user.profile_bio,
            "website": user.profile_website,
            "socials": {
                "vk": user.profile_social_username_vk,
                "tg": user.profile_social_username_tg,
                "gh": user.profile_social_username_gh,
            },
            "privacy": {
                "is_public": user.privacy_profile_public,
                "auth_required": user.privacy_profile_require_auth,
            },
        }

    if include_private_fields:
        if include_email:
            serialized["email"] = user.email
        if include_phone:
            serialized["phone"] = user.phone_number

    if include_optional_fields:
        time_online = user.time_online
        serialized["time_created"] = time.mktime(user.time_created.timetuple())
        serialized["time_online"] = (
            time.mktime(time_online.timetuple()) if time_online else None
        )
        serialized["states"] = {"is_active": user.is_active, "is_vip": user.is_vip}

        if include_private_fields:
            if user.is_admin:
                serialized["states"]["is_admin"] = user.is_admin
            serialized["states"]["is_confirmed"] = user.is_verified

    return serialized if in_list else {"user": serialized}


def serialize_list(
    users: list[User],
    *,
    include_email: bool = False,
    include_optional_fields: bool = False,
    include_private_fields: bool = False,
    include_profile_fields: bool = False,
    include_phone: bool = False,
) -> dict[str, Any]:
    """Returns dict object for API response with serialized users list data."""

    return {
        "users": [
            serialize(
                user,
                in_list=True,
                include_email=include_email,
                include_optional_fields=include_optional_fields,
                include_private_fields=include_private_fields,
                include_profile_fields=include_profile_fields,
                include_phone=include_phone,
            )
            for user in users
        ]
    }


serialize_user = serialize
serialize_users = serialize_list
