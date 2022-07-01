import time


def serialize(oauth_client, display_secret: bool, in_list: bool = False):
    """Returns dict object for API response with serialized OAuth client data."""
    serialized_oauth_client = {
        "id": oauth_client.id,
        "states": {
            "is_active": oauth_client.is_active,
            "is_verified": oauth_client.is_verified,
        },
        "display": {
            "name": oauth_client.display_name,
            "avatar": oauth_client.display_avatar
            if oauth_client.display_avatar
            else "https://oauth.florgon.space/logo192.png",
        },
        "created_at": time.mktime(oauth_client.time_created.timetuple()),
    }

    if display_secret:
        serialized_oauth_client["secret"] = oauth_client.secret

    if in_list:
        return serialized_oauth_client

    return {"oauth_client": serialized_oauth_client}


def serialize_list(
    oauth_clients: list,
    *,
    include_deactivated: bool = False,
    display_secret: bool = False
):
    return {
        "oauth_clients": [
            serialize(oauth_client, display_secret=display_secret, in_list=True)
            for oauth_client in oauth_clients
            if (oauth_client.is_active or include_deactivated)
        ]
    }


serialize_oauth_clients = serialize_list
serialize_oauth_client = serialize
