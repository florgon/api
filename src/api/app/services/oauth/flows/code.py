from app.services.tokens import OAuthCode
from app.services.oauth.permissions import normalize_scope
from app.schemas.oauth import ResponseType, AllowClientModel
from app.database.repositories import OAuthCodesRepository
from app.database.models.user_session import UserSession
from app.database.models.user import User
from app.database.dependencies import Session
from app.config import get_settings


def oauth_authorization_code_flow(
    model: AllowClientModel, db: Session, user: User, session: UserSession
) -> dict:
    # Authorization code flow.
    # Gives code, that required to be decoded using OAuth resolve method at server-side using client secret value.
    # Should be used when there is server-side, which can resolve authorization code.
    # Read more about Florgon OAuth: https://florgon.com/dev/oauth
    assert model.response_type == ResponseType.code
    settings = get_settings()
    # Encoding OAuth code.
    # Code should be resolved at server-side at redirect_uri, using resolve OAuth method.
    # Code should have very small time-to-live (TTL),
    # as it should be resolved to access token with default TTL immediately at server.
    scope = normalize_scope(model.scope)
    time_to_live = settings.security_oauth_code_tokens_ttl
    stored_code = OAuthCodesRepository(db).create(user.id, model.client_id, session.id)  # type: ignore
    code = OAuthCode(
        settings.security_tokens_issuer,
        time_to_live,
        user.id,  # type: ignore
        session.id,  # type: ignore
        scope,
        model.redirect_uri,
        model.client_id,
        code_id=stored_code.id,  # type: ignore
    ).encode(
        key=session.token_secret  # type: ignore
    )

    # Constructing redirect URL with GET query parameters.
    redirect_to = f"{model.redirect_uri}?code={code}&state={model.state}"

    return {
        # Stores URL where to redirect, after allowing specified client,
        # Client should be redirected here, to finish OAuth flow.
        "redirect_to": redirect_to,
        "code": code,
    }
