def build_yandex_oauth_service() -> YandexOauthService:
    """
    Returns Yandex OAuth provider (service).
    """
    settings = get_settings()

    if not settings.auth_ext_oauth_yandex_enabled:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN,
            "Yandex OAuth currently disabled by server administrators.",
        )

    return YandexOauthService(
        client_id=settings.auth_ext_oauth_yandex_client_id,
        client_secret=settings.auth_ext_oauth_yandex_client_secret,
        client_redirect_uri=settings.auth_ext_oauth_yandex_redirect_uri,
        login_hint="",
        force_confirm=True,
    )
