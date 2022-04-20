"""
    Config environment variables reader.
"""

from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    """ Base settings. """
    database_url: str = "postgresql://auth-api:postgres@database/auth-api"

    send_confirmation_email_on_signup: bool = True
    
    oauth_direct_flow_only_verified: bool = True
    oauth_screen_provider_url: str = "https://auth.florgon.space"
    
    jwt_secret: str = "JWT_ANOTHER_SECRET"
    jwt_issuer: str = "localhost"
    jwt_ttl: int = 259200

    cft_secret: str = "CFT_ANOTHER_SECRET"
    cft_salt: str = "CFT_ANOTHER_SALT"
    cft_max_age: int = 3600
    
    proxy_url_prefix: str = ""
    proxy_url_host: str = "http://localhost"

    mail_enabled: bool = False
    mail_from_name: str = ""
    mail_host_server: str = ""
    mail_host_password: str = ""
    mail_host_username: str = ""


@lru_cache()
def get_settings():
    return Settings()
