# pylint: disable=singleton-comparison
"""
    User CRUD utils for the database.
"""

from datetime import datetime

from sqlalchemy.orm import Session
from pyotp import random_base32
from app.services.passwords import get_hashed_password, HashingError
from app.database.models.user import User
from app.config import get_settings


def get_all(db: Session) -> list[User]:
    """
    Returns all users.
    """
    return db.query(User).all()


def get_by_id(db: Session, user_id: int) -> User:
    """Returns user by it`s ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_by_ids(db: Session, user_ids: list[int]) -> list[User]:
    """Returns users by it`s IDs."""
    return db.query(User).filter(User.id.in_(user_ids)).all()


def get_by_username(db: Session, username: str) -> User:
    """Returns user by it`s username."""
    return db.query(User).filter(User.username == username).first()


def email_confirm(db: Session, user: User):
    """Confirms user email."""
    user.is_verified = True
    user.time_verified = datetime.now()

    settings = get_settings()
    if settings.auth_enable_tfa_on_email_verification:
        user.security_tfa_enabled = True
        user.security_tfa_secret_key = random_base32()
    db.commit()


def email_unverify(db: Session, user: User) -> None:
    """Cancels email confirmatiom, made by email_confirm functioin"""
    user.is_verified = False
    user.time_verified = None

    db.commit()


def email_is_taken(db: Session, email: str) -> bool:
    """Returns is given email is taken or not."""
    return db.query(User).filter(User.email == email).first() is not None


def username_is_taken(db: Session, username: str) -> bool:
    """Returns is given username is taken or not."""
    return db.query(User).filter(User.username == username).first() is not None


def phone_number_is_taken(db: Session, phone_number: str) -> bool:
    """Return is given phone number is already taken or not."""
    return db.query(User).filter(User.phone_number == phone_number).first() is not None


def create(db: Session, username: str, email: str, password: str) -> User | None:
    """Creates user with given credentials."""

    # Create new user.
    try:
        hashed_password = get_hashed_password(password, hash_method=None)
    except HashingError:
        return None
    user = User(
        username=username,
        email=email,
        password=hashed_password,
    )

    # Apply user in database.
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_count(db: Session) -> int:
    """Returns total number of users in database."""
    return db.query(User).count()


def get_active_count(db: Session) -> int:
    """Returns total number of active users in database."""
    return db.query(User).filter(User.is_active == True).count()


def get_inactive_count(db: Session) -> int:
    """Returns total number of inactive users in database."""
    return db.query(User).filter(User.is_active == False).count()


def get_last(db: Session) -> User:
    """Returns last created user in database."""
    return db.query(User).order_by(User.time_created.desc()).limit(1).first()


def get_vip_count(db: Session) -> int:
    """Returns total number of vips in database."""
    return db.query(User).filter(User.is_vip == True).count()


def get_admin_count(db: Session) -> int:
    """Returns total number of admin users in database."""
    return db.query(User).filter(User.is_admin == True).count()


def get_verified_count(db: Session) -> int:
    """Returns total number of verified email users in database."""
    return db.query(User).filter(User.is_verified == True).count()
