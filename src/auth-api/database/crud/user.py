"""
    User CRUD utils for the database.
"""

from sqlalchemy.orm import Session

from database.models.user import User


def get_by_id(db: Session, user_id: int) -> User:
    """ Returns user by it`s ID. """
    return db.query(User).filter(User.id == user_id).first()


def create(db: Session, username: str, email: str, password: str) -> User:
    """Creates user with given credentials."""

    # Create new user.
    user = User(username=username, email=email, password=password)

    # Apply user in database.
    db.add(user)
    db.commit()
    db.refresh(user)

    return user