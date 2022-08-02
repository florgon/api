"""
    Base external OAuth provider.
"""

from typing import Literal


class ExternalOAuthService:
    """
    Abstract implementation of external OAuth authentication service.
    """

    # OAuth client configuration.
    client_id = 0
    client_secret = ""
    client_redirect_uri = ""

    # Provider URLs.
    oauth_screen_provider_url = ""
    code_resolver_provider_url = ""
    code_resolver_http_method: Literal["GET", "POST"] = "GET"

    def __init__(self, client_id: str, client_secret: str, client_redirect_uri: str):
        """
        :param client_id: OAuth client ID.
        :param client_secret: OAuth client secret.
        :param client_redirect_uri: OAuth client redirect URI.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_redirect_uri = client_redirect_uri

    def get_authorize_url(self) -> str:
        """
        Returns URL for the OAuth authorization endpoint (Authorization OAuth screen).
        User should be redirected here to proceed authorization process.
        """
        authorize_url_params = self._build_authorize_url_params()
        return f"{self.oauth_screen_provider_url}?{authorize_url_params}&scope="

    def resolve_code_to_token(self, code: str) -> str:
        """
        Resolves code (OAuth) to token (access) by sending requests to auth server.
        """
        return ""

    def get_resolve_code_url(self, code: str) -> str:
        """
        Returns URL for sending request and obtaining OAuth access token from OAuth code.
        """
        resolve_code_url_params = self._build_resolve_code_url_params()
        grant_type = "authorization_code"
        return f"{self.code_resolver_provider_url}?code={code}&grant_type={grant_type}&{resolve_code_url_params}"

    def _build_authorize_url_params(self) -> str:
        """
        Should be inherited and return string of params for authorize url.
        Notice: There should not be `?` or `&` at the beginning.
        """
        return f"client_id={self.client_id}&redirect_uri={self.client_redirect_uri}"

    def _build_resolve_code_url_params(self) -> str:
        """
        Should be inherited and return string of params for resolve code url.
        Notice: `code` param is already sent before!
        Notice: There should not be `?` or `&` at the beginning.
        """
        return f"client_id={self.client_id}&client_secret={self.client_secret}&redirect_uri={self.client_redirect_uri}"
