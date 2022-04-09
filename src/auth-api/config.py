"""
    Config environment variables reader.
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """ Base settings. """
    jwt_secret: str
    jwt_issuer: str
    jwt_ttl: int
    
    class Config:
        env_file = ".env"