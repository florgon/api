"""
    Service to work with users.
"""

from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.database.models.user import User
from app.database.dependencies import Session
from app.database import crud


def query_user_by_id_or_username(
    db: Session, user_id: int | None = None, username: str | None = None
) -> User:
    """Returns user by id or username or raises an exception if failed to query."""
    if user_id is None and username is None:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST, "user_id or username required!"
        )
    if user_id is not None and username is not None:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST, "Please pass only user_id or username!"
        )

    user = (
        crud.user.get_by_id(db, user_id)
        if username is None
        else crud.user.get_by_username(db, username)
    )
    if not user:
        raise ApiErrorException(ApiErrorCode.USER_NOT_FOUND, "User not found!")

    return user
