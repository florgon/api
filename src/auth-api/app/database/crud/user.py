"""
    User CRUD utils for the database.
"""

from sqlalchemy.orm import Session

from app.database.models.user import User


def get_by_id(db: Session, user_id: int) -> User:
    """ Returns user by it`s ID. """
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> User:
    """ Returns user by it`s email. """
    return db.query(User).filter(User.email == email).first()


def get_by_username(db: Session, username: str) -> User:
    """ Returns user by it`s username. """
    return db.query(User).filter(User.username == username).first()


def email_is_taken(db: Session, email: str) -> bool:
    """ Returns is given email is taken or not. """
    return db.query(User).filter(User.email == email).first() is not None


def username_is_taken(db: Session, username: str) -> bool:
    """ Returns is given username is taken or not. """
    return db.query(User).filter(User.username == username).first() is not None


def create(db: Session, username: str, email: str, password: str) -> User:
    """Creates user with given credentials."""

    # Create new user.
    user = User(username=username, email=email, password=password)

    # Apply user in database.
    db.add(user)
    db.commit()
    db.refresh(user)

    return user