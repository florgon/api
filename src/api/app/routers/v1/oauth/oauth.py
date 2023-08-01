"""
    Oauth API auth routers.
"""

from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import Depends, APIRouter
from app.services.request.auth import AuthDataDependency, AuthData
from app.services.oauth.permissions import normalize_scope
from app.services.oauth.flows import oauth_impicit_flow, oauth_authorization_code_flow
from app.services.oauth import resolve_grant, query_oauth_client
from app.services.api import api_success, api_error, ApiErrorCode
from app.schemas.oauth import (
    ResponseType,
    ResolveGrantModel,
    AuthorizeModel,
    AllowClientModel,
)
from app.database.repositories import (
    OAuthClientUserRepository,
    OAuthClientUseRepository,
)
from app.database.dependencies import get_db, Session
from app.config import get_settings, Settings

router = APIRouter()


@router.get("/authorize", deprecated=True)
async def oauth_authorize(
    model: AuthorizeModel = Depends(),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse | RedirectResponse:
    """Redirects to authorization screen."""

    query_oauth_client(db, model.client_id)
    return RedirectResponse(
        url=f"{settings.auth_oauth_screen_provider_url}"
        f"?client_id={model.client_id}"
        f"&state={model.state}"
        f"&redirect_uri={model.redirect_uri}"
        f"&scope={model.scope}"
        f"&response_type={model.response_type}"
    )


@router.get("/accessToken", name="resolve_grant")
async def resolve_grant_from_request(
    model: ResolveGrantModel = Depends(),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """
    Resolves grant to access token.
    """

    return await resolve_grant(
        model=model,
        db=db,
        settings=settings,
    )


@router.get("/allowClient")
async def oauth_allow_client(
    model: AllowClientModel = Depends(),
    auth_data: AuthData = Depends(AuthDataDependency(only_session_token=True)),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Allows access for specified client,
    by returning required information (code or access token) and formatted redirect_to URL.
    """

    oauth_client = query_oauth_client(db=db, client_id=model.client_id)
    user, session = auth_data.user, auth_data.session

    if response := (
        oauth_authorization_code_flow(model, db, user, session)
        if model.response_type == ResponseType.code
        else oauth_impicit_flow(model, user, session)
    ):
        # Log statistics and save oauth user.
        OAuthClientUseRepository(db).create(user.id, oauth_client.id)  # type: ignore
        OAuthClientUserRepository(db).create_if_not_exists(
            user_id=user.id, client_id=oauth_client.id, scope=normalize_scope(model.scope)  # type: ignore
        )
        return api_success(response)

    return api_error(ApiErrorCode.API_UNKNOWN_ERROR, "Failed to finish OAuth process!")
