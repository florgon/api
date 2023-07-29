"""
    Users repository.
"""

from datetime import datetime

from pyotp import random_base32
from app.services.passwords import get_hashed_password, HashingError
from app.schemas.user import UpdateModel
from app.database.repositories.base import BaseRepository
from app.database.models.user import User
from app.config import get_settings


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

    def email_confirm(self, user: User) -> None:
        """Confirms given user email."""

        user.is_verified = True  # type: ignore
        user.time_verified = datetime.now()  # type: ignore

        if get_settings().auth_enable_tfa_on_email_verification:
            user.security_tfa_enabled = True  # type: ignore
            user.security_tfa_secret_key = random_base32()  # type: ignore
        self.db.commit()

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

    def email_is_taken(self, email: str) -> bool:
        """Returns is given email is taken or not."""
        return self.db.query(User).filter(User.email == email).first() is not None

    def username_is_taken(self, username: str) -> bool:
        """Returns is given username is taken or not."""
        return self.db.query(User).filter(User.username == username).first() is not None

    def phone_number_is_taken(self, phone_number: str) -> bool:
        """Return is given phone number is already taken or not."""
        return (
            self.db.query(User).filter(User.phone_number == phone_number).first()
            is not None
        )
