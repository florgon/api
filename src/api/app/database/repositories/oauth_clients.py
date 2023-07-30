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

    def get_by_owner_id(self, owner_id: int) -> list[OAuthClient]:
        """Returns clients by it`s owner ID."""
        return self.db.query(OAuthClient).filter(OAuthClient.owner_id == owner_id).all()

    def expire(self, client: OAuthClient):
        """Re-generates client secret."""
        client.secret = self.generate_secret()  # type: ignore
        self.finish(client)

    def get_by_id(
        self, client_id: int, *, is_active: bool | None = None
    ) -> OAuthClient | None:
        """Returns client by it ID."""
        query = self.db.query(OAuthClient)
        query = query.filter(OAuthClient.id == client_id)
        query = (
            query.filter(OAuthClient.is_active == is_active)
            if is_active is not None
            else query
        )
        return query.first()
