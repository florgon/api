"""
    Florgon API access token implementation.
"""

from .base_token import BaseToken


class AccessToken(BaseToken):
    """
    Access token JWT implementation.

    Used for main authorization, provides access to APIs.
    Issued with OAuth flow.
    Linked with session.
    """

    _type = "access"

    # Custom payload fields.
    _session_id: int = None
    _scope: str = ""

    def get_session_id(self) -> int:
        """Returns session ID linked to the token."""
        return self._session_id

    def get_scope(self) -> str:
        """Returns permissions scope of the token."""
        return self._scope

    def __init__(
        self,
        issuer: str,
        ttl: int | float,
        user_id: int,
        session_id: int | None = None,
        scope: str | None = None,
        payload: dict | None = None,
        *,
        key: str | None = None
    ):
        super().__init__(issuer, ttl, subject=user_id, payload={}, key=key)
        self._session_id = session_id
        self._scope = scope

    @classmethod
    def decode(cls, token: str, key: str | None = None):
        """
        Decoding with custom payload fields.
        """
        instance = super(AccessToken, cls).decode(token, key)
        session_id = instance._raw_payload["sid"]  # pylint: disable=protected-access
        instance._session_id = session_id  # pylint: disable=protected-access
        scope = instance._raw_payload["scope"]  # pylint: disable=protected-access
        instance._scope = scope  # pylint: disable=protected-access
        return instance

    def encode(self, *, key: str | None = None) -> str:
        """
        Encodes token with custom payload fields.
        """
        self.custom_payload["sid"] = self._session_id
        self.custom_payload["scope"] = self._scope
        return super().encode(key=key)
