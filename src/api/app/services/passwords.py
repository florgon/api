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
        return _hash_method_hash_0_sha256(password)
    return _hash_method_hash_1_scrypt(password)


def check_password(
    password: str, hashed_password: str, *, hash_method: int | None = 1
) -> bool:
    """Returns is password and hashed one is same."""
    if not isinstance(password, str) or not isinstance(hashed_password, str):
        raise TypeError("Passwords must be a string!")

    if hash_method == 0:
        return _hash_method_verify_0_sha256(password, hashed_password)
    return _hash_method_verify_1_scrypt(password, hashed_password)


def _hash_method_hash_0_sha256(password: str) -> str:
    """
    Hashes given password.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def _hash_method_verify_0_sha256(password: str, hashed_password: str) -> bool:
    """
    Returns is given password is same with given hash.
    """
    return _hash_method_hash_0_sha256(password) == hashed_password


def _hash_method_hash_1_scrypt(password: str) -> str:
    """
    Hashes given password.
    """

    return _hash_internal_with_scrypt(password, os.urandom(16))


def _hash_method_verify_1_scrypt(password: str, hashed_password: str):
    """
    Returns is given password is same with given hashed_password.
    """
    if hashed_password.count("|") < 2:
        return False

    htype, salt, hash_str = hashed_password.split("|", 2)
    if htype != "_1_scrypt":
        return False
    return _hash_internal_with_scrypt(password, salt.encode("latin-1")) == hash_str


def _hash_internal_with_scrypt(password: str, salt: bytes | None = None) -> str:
    """
    Returns hashed password with scrypt.
    """
    htype = "_1_scrypt"

    if salt is None:
        salt = os.urandom(16)
    hash_bytes = hashlib.scrypt(
        password=password.encode(), salt=salt, n=2**10, r=8, p=1
    )
    return f"{htype}|{salt}|{hash_bytes.decode(encoding='latin-1')}"
