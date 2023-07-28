"""
    Users repository.
"""

from app.services.passwords import get_hashed_password, HashingError
from app.schemas.user import UpdateModel
from app.database.repositories.base import BaseRepository
from app.database.models.user import User


class UsersRepository(BaseRepository):
    """
    Users database CRUD repository.
    """

    def get_user_by_email(self, email: str) -> User | None:
        """
        Get one user by given email.
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> User | None:
        """
        Get one user by given username.
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_login(self, login: str) -> User | None:
        """
        Get one user by given login (username[first check] or email).
        """
        return self.get_user_by_username(username=login) or self.get_user_by_email(
            email=login
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Get one user by ID.
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def deactivate(self, user: User, reason: str | None = None) -> None:
        """
        Deactivates (bans) user.
        TODO: Improve handling of deactivation reasons and etc.
        """
        user.is_active = False  # type: ignore
        reason = reason  # type: ignore

    def activate(self, user: User) -> None:
        """
        Activates (unbans) user.
        """
        user.is_active = True  # type: ignore

    def create(
        self, username: str, email: str, password: str, phone_number: str | None = None
    ) -> User | None:
        """
        Creates new user object that ready to use and have all required stuff (as hashed password) generated.
        """

        try:
            # !TODO!: Weird crutch that is caused by hashing stuff.
            hashed_password = get_hashed_password(password, hash_method=None)
        except HashingError:
            return None

        user = User(
            username=username,
            email=email,
            phone_number=phone_number,
            password=hashed_password,
        )

        self.finish(user)
        return user

    def apply_update_model(self, model: UpdateModel, user: User) -> bool:
        """
        Applies the update model onto given user object.
        """
        new_fields = model.get_new_fields(user)
        for name in new_fields.keys():
            setattr(user, name, getattr(model, name))

        if is_updated := bool(new_fields):
            self.commit()
        return is_updated
