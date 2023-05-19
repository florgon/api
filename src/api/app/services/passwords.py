"""
    Password service for hashing and validating passwords.
"""
import hashlib
import os


class HashingError(Exception):
    pass


def get_hashed_password(password: str, *, hash_method: int | None = 0) -> str:
    """Returns hashed password."""
    if not isinstance(password, str):
        raise TypeError("Password must be a string!")

    if hash_method == 0 or hash_method is None:
        return _hash_method_hash_0_sha256(password)
    return _hash_method_hash_1_scrypt(password, do_verification=True)


def check_password(
    password: str, hashed_password: str, *, hash_method: int | None = 0
) -> bool:
    """Returns is password and hashed one is same."""
    if not isinstance(password, str) or not isinstance(hashed_password, str):
        raise TypeError("Passwords must be a string!")

    if hash_method == 0 or hash_method is None:
        return _hash_method_verify_0_sha256(password, hashed_password)
    return _hash_method_verify_1_scrypt(password, hashed_password)


def _hash_method_hash_0_sha256(password: str) -> str:
    """
    Hashes given password with sha256.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def _hash_method_verify_0_sha256(password: str, hashed_password: str) -> bool:
    """
    Returns is given password is same with given hash.
    """
    return _hash_method_hash_0_sha256(password) == hashed_password


def _hash_method_hash_1_scrypt(password: str, do_verification: bool = True) -> str:
    """
    Hashes given password with random salt.
    """

    if not do_verification:
        return _hash_internal_with_scrypt(password, _generate_encoded_urandom_salt())

    for _ in range(50):
        hashed_password = _hash_internal_with_scrypt(
            password, _generate_encoded_urandom_salt()
        )

        if check_password(password, hashed_password, hash_method=1):
            return hashed_password

    raise HashingError(
        "Failed to hash password, due to reaching limit for re-hashing and can`t get valid hash for the given password!"
    )


def _hash_method_verify_1_scrypt(password: str, hashed_password: str):
    """
    Returns is given password is same with given hashed password.
    """

    if hashed_password.count("\\u") < 2:
        # Not supposed to even hashed with that method.
        return False

    # Getting composed data from hashed password,
    # ommiting hash itself, as it is checks later as full string (including hash)
    htype, salt, _ = hashed_password.split("\\u", 2)
    if htype != "_1_scrypt":
        # Something weird has happened or other hash method.
        return False

    # Should be same as we are using same salt.
    return _hash_internal_with_scrypt(password, salt) == hashed_password


def _hash_internal_with_scrypt(password: str, salt: str | None = None) -> str:
    """
    Returns hashed password with scrypt.
    """

    if salt is None:
        # When there is no salt, this means we want to generate new random salt,
        # otherwise this is verification.
        salt = _generate_encoded_urandom_salt()

    # Hashed password string as "hash_method|salt_for_verification|hash_itself"
    return f"_1_scrypt\\u{salt}\\u{_hash_with_scrypt(password, salt)}"


def _generate_encoded_urandom_salt() -> str:
    """
    Returns encoded (as string) salt for hashing for urandom within bytes range.
    """
    return os.urandom(16).decode("latin-1")


def _hash_with_scrypt(
    password: str, salt: str, *, _bytes_encoding: str = "latin-1"
) -> str:
    """
    Hashes password with given salt using `scrypt` with auto encoding.
    """
    return hashlib.scrypt(
        password=password.encode(),
        salt=salt.encode(_bytes_encoding),
        n=2**10,
        r=8,
        p=1,
    ).decode(encoding=_bytes_encoding)
