"""
    DTO for authentication request.
"""

from app.services.permissions import Permissions, parse_permissions_from_scope

from app.tokens.base_token import BaseToken

from app.database.models.user import User
from app.database.models.user_session import UserSession

class AuthData(object):
    """DTO for authenticated request."""

    user: User
    token: BaseToken
    session: UserSession
    permissions: Permissions | None

    def __init__(
        self,
        token: BaseToken,
        session: UserSession,
        user: User | None = None,
        permissions: Permissions | None = None,
    ) -> None:
        """
        :param user: User database model object.
        :param token: Session or access token object.
        :param session: User session database model object.
        """
        self.user = user
        self.token = token
        self.session = session

        # Parse permission once.
        self.permissions = (
            permissions
            if permissions is not None
            else parse_permissions_from_scope(token.get_scope())
        )
