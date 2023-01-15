"""
    Base external OAuth provider.
"""

from typing import Literal

import requests


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

    def __init__(self, client_id: int, client_secret: str, client_redirect_uri: str):
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

    def resolve_code(self, code: str) -> dict | None:
        """
        Resolves code (OAuth) to response by sending requests to auth server.
        """
        resolve_response = self._request_code_resolver(code=code)

        # Try to process resolver response as JSON.
        try:
            resolve_response_json = resolve_response.json()
        except requests.exceptions.JSONDecodeError:
            return None

        return resolve_response_json

    def resolve_code_to_user_id(self, code: str) -> int | None:
        """
        Returns user id from oauth code by resolving code response.
        """
        resolve_response = self.resolve_code(code=code)
        if resolve_response is None:
            return None
        return resolve_response.get("user_id")

    def get_resolve_code_url(self, code: str) -> str:
        """
        Returns URL for sending request and obtaining OAuth access token from OAuth code.
        """
        resolve_code_url_params = self._build_resolve_code_url_params()
        grant_type = "authorization_code"
        return f"{self.code_resolver_provider_url}?code={code}&grant_type={grant_type}&{resolve_code_url_params}"

    def _request_code_resolver(self, code: str) -> requests.Response:
        """
        Returns response from code resolver OAuth endpoint.
        :param code: OAuth code.
        """
        if self.code_resolver_http_method not in ("GET", "POST"):
            raise ValueError("Code resolver HTTP method must be GET or POST!")

        code_resolver_request_url = self.get_resolve_code_url(code=code)
        if self.code_resolver_http_method == "POST":
            return requests.post(url=code_resolver_request_url)
        return requests.get(url=code_resolver_request_url)

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
