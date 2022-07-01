"""
    Florgon API oauth code (token) implementation.
"""

from ._token import _Token


class OAuthCode(_Token):
    """
        Access token JWT implementation.

        Used for main authorization, provides access to APIs.
        Issued with OAuth flow.
        Linked with session.
    """

    _type = "oauth"

    # Custom payload fields.
    _session_id: int = None
    _redirect_uri: str = ""
    _client_id: int = None
    _scope: str = ""

    def get_session_id(self) -> int:
        return self._session_id

    def get_scope(self) -> str:
        return self._scope

    def get_redirect_uri(self) -> str:
        return self._redirect_uri

    def get_client_id(self) -> int:
        return self._client_id

    def __init__(self, issuer: str, ttl: int | float, user_id: int,
                 session_id: int | None = None, scope: str | None = None,
                 redirect_uri: str | None = None, client_id: int | None = None,
                 payload: dict | None = None, *, key: str | None = None
                 ):
        super().__init__(issuer, ttl, subject=user_id, payload=payload, key=key)
        self._session_id = session_id
        self._scope = scope
        self._redirect_uri = redirect_uri
        self._client_id = client_id

    @classmethod
    def decode(cls, token: str, key: str | None = None):
        """
            Decoding with custom payload fields.
        """
        instance = super(OAuthCode, cls).decode(token, key)
        instance._session_id = instance._raw_payload["sid"]
        instance._scope = instance._raw_payload["scope"]
        instance._redirect_uri = instance._raw_payload["ruri"]
        instance._client_id = instance._raw_payload["cid"]
        return instance

    def encode(self, *, key: str | None = None) -> str:
        """
            Encodes token with custom payload fields.
        """
        self.custom_payload["sid"] = self._session_id
        self.custom_payload["ruri"] = self._redirect_uri
        self.custom_payload["scope"] = self._scope
        self.custom_payload["cid"] = self._client_id
        return super().encode(key=key)
