"""
    Bootstrap database with first queries.
    Used for creating initial database entries like initial OAuth client and super user.
"""

from time import sleep

from sqlalchemy.exc import OperationalError
from sqlalchemy import select
from app.database.repositories.users import UsersRepository
from app.database.repositories.oauth_clients import OAuthClientsRepository
from app.database.dependencies import SessionLocal, Session
from app.config import get_settings, get_logger


def create_start_database_entries() -> None:
    """
    Creates initial OAuth client and super user for first time.
    """
    db = SessionLocal()
    _create_superuser_if_not_exists(db=db)
    _create_initial_oauth_client_if_not_exists(db=db)
    db.close()


def wait_for_database_startup() -> None:
    """
    Used for checking that database is up, running and ready to execute statements.
    """
    try:
        db = SessionLocal()
        db.execute(select(1))
        db.close()
    except OperationalError:
        get_logger().warning(
            "[database] Database is starting up! Waiting next 1 second."
        )
        sleep(1)
        wait_for_database_startup()


def _create_superuser_if_not_exists(db: Session) -> None:
    """
    Simple INSERT IF NOT EXISTS for super user entry.
    """

    settings = get_settings()
    repo = UsersRepository(db=db)
    user = repo.get_user_by_username(username=settings.superuser_username)
    if user:
        return

    get_logger().info(
        "[database_bootstrap] Creating superuser as not found it in the database..."
    )
    user = None
    while user is None:
        # !TODO!: This crutch is temporary, caused by some hashing problems.
        user = repo.create(
            username=settings.superuser_username,
            email=settings.superuser_email,
            password=settings.superuser_password,
        )
    user.is_admin = True  # type: ignore
    user.is_verified = True  # type: ignore
    repo.finish(user)


def _create_initial_oauth_client_if_not_exists(db: Session) -> None:
    """
    Simple INSERT IF NOT EXISTS for initial OAuth client.
    Linked with user that has `superuser_id` (super user, first user).
    """
    repo = OAuthClientsRepository(db=db)
    client = repo.get_client_by_id(client_id=1)
    if client:
        return

    get_logger().info(
        "[database_bootstrap] Creating initial OAuth client as not found it in the database..."
    )
    user = UsersRepository(db=db).get_user_by_id(user_id=get_settings().superuser_id)
    if not user:
        get_logger().warning(
            "[database_bootstrap] Skipped creating initial OAuth client as not found super user with id=1!"
        )
        return
    client = repo.create(
        owner_id=user.id,  # type: ignore
        display_name="[Initial Client]",
    )
    client.is_verified = True  # type: ignore
    repo.finish(client)
