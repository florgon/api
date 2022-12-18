"""
    Bootstrap database with first queries.
"""
from app.config import get_settings
from app.database.dependencies import Session, get_db_as_session
from app.database.repositories.users import UsersRepository


def create_start_database_entries() -> None:
    """
    Creates startup database entries by query database.
    """
    db = get_db_as_session()
    _create_superuser_if_not_exists(db=db)


def _create_superuser_if_not_exists(db: Session) -> None:
    """
    Creates super user if it is not found in the database.
    """
    settings = get_settings()
    repo = UsersRepository(db=db)
    user = repo.get_user_by_username(settings.superuser_username)
    if not user:
        user = repo.create(
            username=settings.superuser_username,
            email=settings.superuser_email,
            password=settings.superuser_password,
        )
        user.is_admin = True
        user.is_verified = True
        repo.db.add(user)
        repo.db.commit()
        repo.db.refresh(user)
