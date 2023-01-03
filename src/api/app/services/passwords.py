"""
    Password service for hashing and validating passwords.
"""
import hashlib
import os


def get_hashed_password(password: str, *, hash_method: int | None = 1) -> str:
    """Returns hashed password."""
    if not isinstance(password, str):
        raise TypeError("Password must be a string!")

    if hash_method == 0:
        return hashlib.sha256(password.encode()).hexdigest()
    if hash_method == 1:
        # Latest hash method.
        pass
    return hashlib.scrypt(
        password=password.encode(), salt=os.urandom(16), n=2**10, r=8, p=1
    ).decode(encoding="latin-1")


def check_password(
    password: str, hashed_password: str, *, hash_method: int | None = 1
) -> bool:
    """Returns is password and hashed one is same."""

    if hash_method == 0:
        return get_hashed_password(password, hash_method=hash_method) == hashed_password
    if hash_method == 1:
        # Latest hash method.
        pass
    return get_hashed_password(password, hash_method=hash_method) == hashed_password
