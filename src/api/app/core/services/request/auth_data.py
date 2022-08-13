"""
    DTO for authentication request.
"""

from app.core.database.models.user import User
from app.core.database.models.user_session import UserSession
from app.core.services.permissions import Permission, parse_permissions_from_scope
from app.core.tokens import BaseToken


class AuthData:
    """DTO for authenticated request."""

    user: User
    token: BaseToken
    session: UserSession
    permissions: list[Permission] | None

    def __init__(
        self,
        token: BaseToken,
        session: UserSession,
        user: User | None = None,
        permissions: list[Permission] | None = None,
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
