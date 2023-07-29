"""
    OAuth Client user repository.
"""


from app.database.repositories.base import BaseRepository
from app.database.models.oauth_client_user import OAuthClientUser


class OAuthClientUserRepository(BaseRepository):
    """
    OAuth client user database CRUD repository.
    """

    def create_if_not_exists(
        self, user_id: int, client_id: int, scope: str
    ) -> OAuthClientUser:
        """Creates new OAuth client user object that is committed in the database already if not found."""

        oauth_client_user = (
            self.db.query(OAuthClientUser)
            .filter(OAuthClientUser.client_id == client_id)
            .filter(OAuthClientUser.user_id == user_id)
            .first()
        )

        if not oauth_client_user:
            oauth_client_user = OAuthClientUser(
                user_id=user_id, client_id=client_id, requested_scope=scope
            )
            self.finish(oauth_client_user)

        if (
            not oauth_client_user.is_active
            or oauth_client_user.requested_scope != scope  # type: ignore
        ):
            oauth_client_user.requested_scope = scope  # type: ignore
            oauth_client_user.is_active = True  # type: ignore
            self.finish(oauth_client_user)

        return oauth_client_user

    def get_by_user_id(self, user_id: int) -> list[OAuthClientUser]:
        """Returns all oauth client users by user ID."""
        return (
            self.db.query(OAuthClientUser)
            .filter(OAuthClientUser.is_active == True)
            .filter(OAuthClientUser.user_id == user_id)
            .all()
        )

    def get_by_client_and_user_id(
        self, user_id: int, client_id: int
    ) -> OAuthClientUser | None:
        """Returns oauth client user by user and client ID."""
        return (
            self.db.query(OAuthClientUser)
            .filter(OAuthClientUser.is_active == True)
            .filter(OAuthClientUser.user_id == user_id)
            .filter(OAuthClientUser.client_id == client_id)
            .first()
        )
