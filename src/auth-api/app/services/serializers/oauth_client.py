def serialize(oauth_client):
    """Returns dict object for API response with serialized OAuth client data."""
    return {
        "oauth_client": {
            "id": oauth_client.id,
            "secret": oauth_client.secret,
            "states": {
                "is_active": oauth_client.is_active,
                "is_verified": oauth_client.is_verified,
            }
        }
    }
