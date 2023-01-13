"""
    OAuth Client repository.
"""

from secrets import token_urlsafe
from app.database.models.oauth_client import OAuthClient
from app.database.repositories.base import BaseRepository


class OAuthClientsRepository(BaseRepository):
    """
    OAuth client database CRUD repository.
    """

    def get_client_by_id(self, client_id: int) -> OAuthClient | None:
        """Returns client by ID."""
        return self.db.query(OAuthClient).filter(OAuthClient.id == client_id).first()

    @staticmethod
    def generate_secret() -> str:
        """Returns generated client secret for OAuth client."""
        return token_urlsafe(32)

    def create(self, owner_id: int, display_name: str) -> OAuthClient:
        """Creates new oauth client."""
        oauth_client = OAuthClient(
            secret=self.generate_secret(), owner_id=owner_id, display_name=display_name
        )

        self.db.add(oauth_client)
        self.db.commit()
        self.db.refresh(oauth_client)
        return oauth_client
