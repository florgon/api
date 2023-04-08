"""
    Bootstrap database with first queries.
"""
from app.database.repositories.users import UsersRepository
from app.database.repositories.oauth_clients import OAuthClientsRepository, OAuthClient
from app.database.dependencies import SessionLocal, Session
from app.config import get_logger

SUPERUSER_USER_ID = 1
SUPERUSER_USERNAME = "admin"
SUPERUSER_PASSWORD = "adminadmin"
SUPERUSER_EMAIL = "admin@admin.com"


def create_start_database_entries() -> None:
    """
    Creates startup database entries by query database.
    """
    db = SessionLocal()
    _create_superuser_if_not_exists(db=db)
    _create_initial_oauth_client_if_not_exists(db=db)
    db.close()


def _create_superuser_if_not_exists(db: Session) -> None:
    """
    Creates super user if it is not found in the database.
    """
    repo = UsersRepository(db=db)
    user = repo.get_user_by_username(username=SUPERUSER_USERNAME)
    if not user:
        get_logger().info(
            "[database_bootstrap] Creating superuser as not found it in the database..."
        )
        user = None
        while user is None:
            user = repo.create(
                username=SUPERUSER_USERNAME,
                email=SUPERUSER_EMAIL,
                password=SUPERUSER_PASSWORD,
            )
        user.is_admin = True
        user.is_verified = True
        repo.db.add(user)
        repo.db.commit()
        repo.db.refresh(user)


def _create_initial_oauth_client_if_not_exists(db: Session) -> None:
    """
    Creates initial base OAuth client if it is not found in the database.
    Linked with user that has id `SUPERUSER_USER_ID` (super user, first user).
    """
    repo = OAuthClientsRepository(db=db)
    client = repo.get_client_by_id(client_id=1)
    if not client:
        get_logger().info(
            "[database_bootstrap] Creating initial oauth client as not found it in the database..."
        )
        user = UsersRepository(db=db).get_user_by_username(username=SUPERUSER_USERNAME)
        if not user:
            get_logger().warn(
                "[database_bootstrap] Skipped creating initial oauth client as not found super user with id=1!"
            )
            return
        client: OAuthClient = repo.create(
            owner_id=user.id,
            display_name="OAuth",
        )
        client.is_verified = True
        repo.db.add(client)
        repo.db.commit()
        repo.db.refresh(client)
