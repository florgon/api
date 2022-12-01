from app.database.dependencies import Session
from app.database.models.user import User
from .base import BaseRepository


class UsersRepository(BaseRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_user_by_email(self, email: str) -> User | None:
        """Returns user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> User | None:
        """Returns user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_username(self, username: str) -> User | None:
        """Returns user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_login(self, login: str) -> User | None:
        """Returns user by login."""
        user = self.get_user_by_username(username=login)
        if not user:
            return self.get_user_by_email(email=login)
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        """Returns user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
