"""
    OAuth Client use repository.
"""


from app.database.repositories.base import BaseRepository
from app.database.models.oauth_client_use import OAuthClientUse


class OAuthClientUseRepository(BaseRepository):
    """
    OAuth client use database CRUD repository.
    """

    def create(self, user_id: int, client_id: int) -> OAuthClientUse:
        """
        Creates new client use object that ready to use and have all required stuff (as secret) generated.
        """
        oauth_client_use = OAuthClientUse(user_id=user_id, client_id=client_id)

        self.finish(oauth_client_use)
        return oauth_client_use

    def get_unique_users(self, client_id: int) -> int:
        """Returns count of all uses of oauth client by different users."""
        return (
            self.db.query(OAuthClientUse.user_id)
            .filter(OAuthClientUse.client_id == client_id)
            .group_by(OAuthClientUse.user_id)
            .count()
        )

    def get_uses(self, client_id: int) -> int:
        """Returns count of all uses of oauth client."""
        return (
            self.db.query(OAuthClientUse)
            .filter(OAuthClientUse.client_id == client_id)
            .count()
        )
