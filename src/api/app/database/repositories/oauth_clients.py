"""
    OAuth Client repository.
"""

from secrets import token_urlsafe

from app.database.repositories.base import BaseRepository
from app.database.models.oauth_client import OAuthClient


class OAuthClientsRepository(BaseRepository):
    """
    OAuth client database CRUD repository.
    """

    def get_client_by_id(self, client_id: int) -> OAuthClient | None:
        """
        Get one client by given id.
        """
        return self.db.query(OAuthClient).filter(OAuthClient.id == client_id).first()

    @staticmethod
    def generate_secret() -> str:
        """
        Generate standartized secret key for the new client.
        """
        return token_urlsafe(32)

    def create(self, owner_id: int, display_name: str) -> OAuthClient:
        """
        Creates new client object that ready to use and have all required stuff (as secret) generated.
        """
        oauth_client = OAuthClient(
            secret=self.generate_secret(), owner_id=owner_id, display_name=display_name
        )

        self.finish(oauth_client)
        return oauth_client
