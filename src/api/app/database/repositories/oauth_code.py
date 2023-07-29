"""
    OAuth code repository.
"""


from app.database.repositories.base import BaseRepository
from app.database.models.oauth_code import OAuthCode


class OAuthCodesRepository(BaseRepository):
    """
    OAuth code CRUD repository.
    """

    def create(self, user_id: int, client_id: int, session_id: int) -> OAuthCode:
        """Creates new OAuth code object that is committed in the database already."""
        oauth_code = OAuthCode(
            user_id=user_id, client_id=client_id, session_id=session_id
        )
        self.finish(oauth_code)
        return oauth_code

    def get_by_id(self, code_id: int) -> OAuthCode | None:
        """Returns oauth code by id."""
        return self.db.query(OAuthCode).filter(OAuthCode.id == code_id).first()
