"""
    GitHub external OAuth service.
"""

from ._base import ExternalOAuthService


class GithubOauthService(ExternalOAuthService):
    """
    GitHub external OAuth service.
    """

    def __init__(self, client_id: str, client_secret: str, client_redirect_uri: str):
        """
        :param client_id: OAuth client ID.
        :param client_secret: OAuth client secret.
        :param client_redirect_uri: OAuth redirect URI.
        """
        super().__init__(client_id, client_secret, client_redirect_uri)

        # Providers.
        self.code_resolver_http_method = "POST"
        self.oauth_screen_provider_url = "https://github.com/login/oauth/authorize"
        self.code_resolver_provider_url = "https://github.com/login/oauth/access_token"
