"""
    Password service for hashing and validating passwords.
"""
import hashlib


def get_hashed_password(password: str) -> str:
    """ Returns hashed password. """
    assert isinstance(password, str)
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password: str, hashed_password: str) -> bool:
    """ Returns is password and hashed one is same. """
    return get_hashed_password(password) == hashed_password
