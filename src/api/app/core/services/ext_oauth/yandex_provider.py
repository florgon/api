"""
    Yandex external OAuth service.
"""

from ._base import ExternalOAuthService


class YandexOauthService(ExternalOAuthService):
    """
    Yandex external OAuth service.
    """

    # Additional fields.
    login_hint: str = ""
    force_confirm: bool = True

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        client_redirect_uri: str,
        login_hint: str = "",
        force_confirm: bool = True,
    ):
        """
        :param client_id: OAuth client ID.
        :param client_secret: OAuth client secret.
        :param client_redirect_uri: OAuth redirect URI.
        :param login_hint: Login hint as username or login.
        :param force_confirm: Should page shown even not required (Already granted permissions).
        """
        super().__init__(client_id, client_secret, client_redirect_uri)

        # Providers.
        self.code_resolver_http_method = "POST"
        self.oauth_screen_provider_url = "https://oauth.yandex.ru/authorize"
        self.code_resolver_provider_url = "https://oauth.yandex.ru"

        # Params.
        self.login_hint = login_hint
        self.force_confirm = force_confirm

    def _build_authorize_url_params(self):
        """Build authorization url params."""
        force_confirm = "yes" if self.force_confirm else "no"
        response_type = "code"
        return f"client_id={self.client_id}&redirect_uri={self.client_redirect_uri}&login_hint={self.login_hint}&force_confirm={force_confirm}&response_type={response_type}"
