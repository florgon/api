"""
    Config environment variables reader.
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """ Base settings. """
    jwt_secret: str = "JWT_ANOTHER_SECRET"
    jwt_issuer: str = "florgon.space"
    jwt_ttl: int = 259200

    cft_secret: str = "CFT_ANOTHER_SECRET"
    cft_salt: str = "CFT_ANOTHER_SALT"

    proxy_url_prefix: str = ""
    proxy_url_host: str = "http://localhost"

    mail_from_name: str = "Florgon Auth"
    mail_host_server: str = ""
    mail_host_password: str = ""
    mail_host_username: str = ""

