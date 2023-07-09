"""
    OAuth client database model serializer.
"""


import time


def serialize(oauth_client, display_secret: bool, in_list: bool = False):
    """Returns dict object for API response with serialized OAuth client data."""
    serialized = {
        "id": oauth_client.id,
        "states": {
            "is_active": oauth_client.is_active,
            "is_verified": oauth_client.is_verified,
        },
        "display": {
            "name": oauth_client.display_name,
            # TODO: Refactor that default display url.
            "avatar_url": oauth_client.display_avatar
            or "https://florgon.com/logo192.png",
        },
        "created_at": time.mktime(oauth_client.time_created.timetuple()),
    }

    serialized["display"]["avatar"] = serialized["display"]["avatar_url"]
    if display_secret:
        serialized["secret"] = oauth_client.secret

    return serialized if in_list else {"oauth_client": serialized}


def serialize_list(
    oauth_clients: list,
    *,
    include_deactivated: bool = False,
    display_secret: bool = False
):
    """Returns dict object for API response with serialized oauth clients list data."""

    return {
        "oauth_clients": [
            serialize(oauth_client, display_secret=display_secret, in_list=True)
            for oauth_client in oauth_clients
            if (oauth_client.is_active or include_deactivated)
        ]
    }


serialize_oauth_clients = serialize_list
serialize_oauth_client = serialize
