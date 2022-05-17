"""
    Config environment variables reader.
"""

from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    """ Base settings. """
    database_url: PostgresDsn

    oauth_screen_provider_url: str
    
    jwt_issuer: str
    jwt_secert: str

    access_token_jwt_ttl: int
    session_token_jwt_ttl: int
    oauth_code_jwt_ttl: int

    cft_secret: str
    cft_salt: str
    cft_max_age: int
    
    proxy_url_prefix: str
    proxy_url_host: str

    mail_enabled: bool
    mail_from_name: str
    mail_host_server: str
    mail_host_password: str
    mail_host_username: str

_settings = Settings()

def get_settings():
    return _settings
