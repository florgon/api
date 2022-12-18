"""
    Bootstrap database with first queries.
"""
from app.database.dependencies import Session, SessionLocal
from app.database.repositories.users import UsersRepository
from app.database.repositories.oauth_clients import OAuthClientsRepository, OAuthClient


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
    user = repo.get_user_by_username(username="admin")
    if not user:
        user = repo.create(
            username="admin",
            email="admin@admin.com",
            password="admin",
        )
        user.is_admin = True
        user.is_verified = True
        repo.db.add(user)
        repo.db.commit()
        repo.db.refresh(user)


def _create_initial_oauth_client_if_not_exists(db: Session) -> None:
    """
    Creates initial base OAuth client if it is not found in the database.
    Linked with user that has id 1 (super user, first user).
    """
    repo = OAuthClientsRepository(db=db)
    client = repo.get_client_by_id(client_id=1)
    if not client:
        client: OAuthClient = repo.create(owner_id=1, display_name="OAuth")
        client.is_verified = True
        repo.db.add(client)
        repo.db.commit()
        repo.db.refresh(client)
