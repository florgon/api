"""
    DTO for authentication request.
"""

from app.services.tokens import BaseToken, AccessToken
from app.services.permissions import parse_permissions_from_scope, Permission
from app.database.models.user_session import UserSession
from app.database.models.user import User


class AuthData:
    """DTO for authenticated request."""

    user: User
    token: BaseToken
    session: UserSession
    permissions: set[Permission] | None

    def __init__(
        self,
        token: BaseToken,
        session: UserSession,
        user: User | None = None,
        permissions: set[Permission] | None = None,
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
        self.permissions = _get_permissions_from_token_or_default(permissions, token)


def _get_permissions_from_token_or_default(
    permissions: set[Permission] | None,
    token: BaseToken,
) -> set[Permission]:
    """
    Parses permission from access token or returns default / empty set if cannot get.
    """
    if permissions is None:
        if isinstance(token, AccessToken):
            return parse_permissions_from_scope(token.get_scope())
        return set()
    if not isinstance(permissions, set):
        raise TypeError("Permissions for AuthData should be set of the permissions!")
    return permissions
