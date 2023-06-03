"""
    VK external OAuth service.
"""

from ._base import ExternalOAuthService


class VkOauthService(ExternalOAuthService):
    """
    VK external OAuth service.
    """

    # Additional fields.
    display: str = "page"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        client_redirect_uri: str,
        display: str | None = None,
    ):
        """
        :param client_id: OAuth client ID.
        :param client_secret: OAuth client secret.
        :param client_redirect_uri: OAuth redirect URI.
        :param display: OAuth screen provider display screen type.
        """
        super().__init__(client_id, client_secret, client_redirect_uri)

        # Providers.
        self.code_resolver_http_method = "GET"
        self.oauth_screen_provider_url = "https://oauth.vk.com/authorize"
        self.code_resolver_provider_url = "https://oauth.vk.com/access_token"

        # Params.
        self.display = display if display is not None else "page"

    def _build_authorize_url_params(self):
        """Build authorization url params."""
        response_type = "code"
        return f"client_id={self.client_id}&redirect_uri={self.client_redirect_uri}&display={self.display}&response_type={response_type}"
