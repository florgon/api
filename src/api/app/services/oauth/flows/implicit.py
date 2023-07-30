from app.services.tokens import AccessToken
from app.services.oauth.permissions import (
    permissions_get_ttl,
    parse_permissions_from_scope,
    normalize_scope,
    Permission,
)
from app.schemas.oauth import ResponseType, AllowClientModel
from app.database.models.user_session import UserSession
from app.database.models.user import User
from app.config import get_settings


def oauth_impicit_flow(
    model: AllowClientModel, user: User, session: UserSession
) -> dict:
    """
    Implicit authorization flow.
    Simply, gives access token inside hash-link.
    Should be used when there is no server-side, which can resolve authorization code.
    Read more about Florgon OAuth: https://florgon.com/dev/oauth
    """
    assert model.response_type == ResponseType.token
    settings = get_settings()

    # Encoding access token.
    # Access token have infinity TTL, if there is scope permission given for no expiration date.
    access_token_permissions = parse_permissions_from_scope(model.scope)
    access_token_ttl = permissions_get_ttl(
        access_token_permissions, default_ttl=settings.security_access_tokens_ttl
    )

    access_token = AccessToken(
        settings.security_tokens_issuer,
        access_token_ttl,
        user.id,  # type: ignore
        session.id,  # type: ignore
        normalize_scope(model.scope),
    ).encode(
        key=session.token_secret  # type: ignore
    )

    # Constructing redirect URL with hash-link parameters.
    # Email field should be passed only if OAuth client requested given scope permission.
    redirect_to_email_param = (
        f"&email={user.email}" if Permission.email in access_token_permissions else ""
    )
    redirect_to = (
        f"{model.redirect_uri}"
        f"#token={access_token}"
        f"&user_id={user.id}"
        f"&state={model.state}"
        f"&expires_in={access_token_ttl}{redirect_to_email_param}"
    )

    return {
        # Stores URL where to redirect, after allowing specified client,
        # Client should be redirected here, to finish OAuth flow.
        "redirect_to": redirect_to,
        "access_token": access_token,
    }
