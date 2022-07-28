"""
    User CRUD utils for the database.
"""

# Libraries.
from datetime import datetime
from sqlalchemy.orm import Session

# Services.
from app.database.models.user import User
from app.services.passwords import get_hashed_password
from app.config import get_settings


def get_by_id(db: Session, user_id: int) -> User:
    """Returns user by it`s ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> User:
    """Returns user by it`s email."""
    return db.query(User).filter(User.email == email).first()


def get_by_username(db: Session, username: str) -> User:
    """Returns user by it`s username."""
    return db.query(User).filter(User.username == username).first()


def get_by_login(db: Session, login: str) -> User:
    """Returns user by it`s login."""
    user = get_by_username(db=db, username=login)
    if not user:
        return get_by_email(db=db, email=login)
    return user


def email_confirm(db: Session, user: User):
    """Confirms user email."""
    settings = get_settings()
    user.is_verified = True
    user.time_verified = datetime.now()
    user.security_tfa_enabled = settings.user_enable_email_tfa_by_default
    db.commit()


def email_is_taken(db: Session, email: str) -> bool:
    """Returns is given email is taken or not."""
    return db.query(User).filter(User.email == email).first() is not None


def username_is_taken(db: Session, username: str) -> bool:
    """Returns is given username is taken or not."""
    return db.query(User).filter(User.username == username).first() is not None


def create(db: Session, username: str, email: str, password: str) -> User:
    """Creates user with given credentials."""

    # Create new user.
    user = User(username=username, email=email, password=get_hashed_password(password))

    # Apply user in database.
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_count(db: Session) -> int:
    return db.query(User).count()


def get_active_count(db: Session) -> int:
    return db.query(User).filter(User.is_active == True).count()


def get_inactive_count(db: Session) -> int:
    return db.query(User).filter(User.is_active == False).count()


def get_last(db: Session) -> User:
    return db.query(User).order_by(User.time_created.desc()).limit(1).first()


def get_vip_count(db: Session) -> int:
    return db.query(User).filter(User.is_vip == True).count()


def get_verified_count(db: Session) -> int:
    return db.query(User).filter(User.is_verified == True).count()
