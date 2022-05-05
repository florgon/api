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
            "avatar": oauth_client.display_avatar if oauth_client.display_avatar else "https://auth.florgon.space/logo192.png",
        }
    }
    
    if display_secret:
        serialized_oauth_client["secret"] = oauth_client.secret
 
    if in_list:
        return serialized_oauth_client
        
    return {
        "oauth_client": serialized_oauth_client
    }