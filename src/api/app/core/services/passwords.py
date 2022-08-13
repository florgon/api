"""
    Password service for hashing and validating passwords.
"""
import hashlib


def get_hashed_password(password: str) -> str:
    """Returns hashed password."""
    if not isinstance(password, str):
        raise TypeError("Password must be a string!")

    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password: str, hashed_password: str) -> bool:
    """Returns is password and hashed one is same."""
    return get_hashed_password(password) == hashed_password
