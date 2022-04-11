"""
    Config environment variables reader.
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """ Base settings. """
    jwt_secret: str
    jwt_issuer: str
    jwt_ttl: int

    proxy_url_prefix: str = ""

    mail_from_name: str
    mail_host_server: str
    mail_host_password: str
    mail_host_username: str

    class Config:
        env_file = ".env"