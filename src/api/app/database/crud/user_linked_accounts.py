# pylint: disable=singleton-comparison
"""
    User linked accounts CRUD utils for the database.
"""

from sqlalchemy.orm import Session

from app.database.models.user_linked_accounts import UserLinkedAccounts


def create(
    db: Session,
    user_id: int,
    vk_user_id: int | None = None,
    vk_user_email: str | None = None,
    github_user_id: int | None = None,
    github_user_email: str | None = None,
    yandex_user_id: int | None = None,
    yandex_user_email: str | None = None,
) -> UserLinkedAccounts:
    """Creates new user linked accounts object that is committed in the database already."""
    user_linked_accounts = UserLinkedAccounts(
        user_id=user_id,
        vk_user_id=vk_user_id,
        vk_user_email=vk_user_email,
        github_user_id=github_user_id,
        github_user_email=github_user_email,
        yandex_user_id=yandex_user_id,
        yandex_user_email=yandex_user_email,
    )
    db.add(user_linked_accounts)
    db.commit()
    db.refresh(user_linked_accounts)
    return user_linked_accounts


def get_or_create_by_user_id(db: Session, user_id: int) -> UserLinkedAccounts:
    """Creates or returns already created user agent."""
    user_linked_accounts = get_by_user_id(db, user_id=user_id)
    if user_linked_accounts is None:
        # By default that will be empty without any linked accounts.
        user_linked_accounts = UserLinkedAccounts(user_id=user_id)
        db.add(user_linked_accounts)
        db.commit()
        db.refresh(user_linked_accounts)
    return user_linked_accounts


def get_by_id(db: Session, user_linked_accounts_id: int) -> UserLinkedAccounts | None:
    """Returns user linked accounts by id."""
    return (
        db.query(UserLinkedAccounts)
        .filter(UserLinkedAccounts.id == user_linked_accounts_id)
        .first()
    )


def get_by_user_id(db: Session, user_id: int) -> UserLinkedAccounts | None:
    """Returns user linked accounts by user id."""
    return db.query(UserLinkedAccounts).filter(UserLinkedAccounts.id == user_id).first()
