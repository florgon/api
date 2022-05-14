"""
    User CRUD utils for the database.
"""

# Libraries.
from sqlalchemy.orm import Session

# Services.
from app.database.models.user import User
from app.services.passwords import get_hashed_password

def get_by_id(db: Session, user_id: int) -> User:
    """ Returns user by it`s ID. """
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> User:
    """ Returns user by it`s email. """
    return db.query(User).filter(User.email == email).first()


def get_by_username(db: Session, username: str) -> User:
    """ Returns user by it`s username. """
    return db.query(User).filter(User.username == username).first()


def get_by_login(db: Session, login: str) -> User:
    """ Returns user by it`s login. """
    user = get_by_username(db=db, username=login)
    if not user:
        return get_by_email(db=db, email=login)
    return user

def email_confirm(db: Session, user: User):
    """ Confirms user email. """
    user.is_verified = True
    db.commit()

def email_is_taken(db: Session, email: str) -> bool:
    """ Returns is given email is taken or not. """
    return db.query(User).filter(User.email == email).first() is not None


def username_is_taken(db: Session, username: str) -> bool:
    """ Returns is given username is taken or not. """
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