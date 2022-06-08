"""
    Florgon API sessiion token implementation.
"""

from ._token import _Token


class SessionToken(_Token):
    """
        Session token JWT implementation.

        Used to issue new access tokens.
        Root token for Florgon core authorization process.
        Linked with session.
    """

    _type = "session"

    # Custom payload fields.
    _session_id: int = None

    def get_session_id(self) -> int:
        return self._session_id

    def __init__(self, issuer: str, ttl: int | float, user_id: int, \
        session_id: int | None = None, \
            payload: dict | None = None, *, key: str | None = None
    ):
        super().__init__(issuer, ttl, subject=user_id, payload={}, key=key)
        self._session_id = session_id

    @classmethod
    def decode(cls, token: str, key: str | None = None):
        """
            Decoding with custom payload fields.
        """
        instance = super(SessionToken, cls).decode(token, key)
        instance._session_id = instance._raw_payload["sid"]
        return instance

    def encode(self, *, key: str | None = None) -> str:
        """
            Encodes token with custom payload fields.
        """
        self.custom_payload["sid"] = self._session_id
        return super().encode(key=key)
