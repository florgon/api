"""
    Auth API auth routers.
"""

# Libraries.
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

# Services.
from app import services
from app.services import serializers
from app.services.api.errors import ApiErrorCode
from app.services.api.response import (
    api_error,
    api_success
)

# Other.
from app import database
from app.database import crud
from app.email import messages
from app.config import (
    Settings, get_settings
)

# Database dependency.
get_db = database.dependencies.get_db

# Fast API router.
router = APIRouter()


@router.get("/signup")
async def signup(username: str, email: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ API endpoint to signup and create new user. """

    # Try validate request for fields.
    is_valid, validation_error = services.validators.user.validate_signup_fields(db, username, email, password)
    if not is_valid:
        return validation_error

    # Create new user.
    password = services.passwords.get_hashed_password(password)
    user = crud.user.create(db=db, email=email, username=username, password=password)
    token = services.jwt.encode(user, settings.jwt_issuer, settings.jwt_ttl, settings.jwt_secret)

    # Send email.
    confirmation_link = services.cftokens.generate_confirmation_token(user.email, settings.cft_secret, settings.cft_salt, settings.proxy_url_host, settings.proxy_url_prefix)
    await messages.send_verification_email(user.email, user.username, confirmation_link)

    # Return user with token.
    return api_success({
        **serializers.user.serialize(user),
        "token": token
    })


@router.get("/signin")
async def signin(login: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ API endpoint to signin and get token. """

    # Query user.
    user = crud.user.get_by_login(db=db, login=login)

    # Check credentials.
    if not user or not services.passwords.check_password(password=password, hashed_password=user.password):
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid credentials")

    # Generate token.
    token = services.jwt.encode(user, settings.jwt_issuer, settings.jwt_ttl, settings.jwt_secret)

    # Return user with token.
    return api_success({
        **serializers.user.serialize(user),
        "token": token
    })


@router.get("/oauth/direct")
async def oauth_direct(client_id: int, client_secret: str, login: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for direct oauth authorization (Should be dissalowed by external clients). """

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification for OAuth client.
    if not oauth_client:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "OAuth client not found!")
    if oauth_client.secret != client_secret:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid OAuth client secret.")
    if not oauth_client.is_verified:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Given OAuth client is not verified, and forbidden to use direct OAUTH!")

    # Query user.
    user = crud.user.get_by_login(db=db, login=login)

    # Check credentials.
    if not user or not services.passwords.check_password(password=password, hashed_password=user.password):
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid credentials")

    # Generate token.
    token = services.jwt.encode(user, settings.jwt_issuer, settings.jwt_ttl, settings.jwt_secret)

    # Return user with token.
    return api_success({
        **serializers.user.serialize(user),
        "token": token
    })

@router.get("/oauth/client/new")
async def oauth_client_new(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for creating new oauth authorization client. """

    # Try authenticate.
    is_authenticated, token_payload_or_error, _ = services.request.try_decode_token_from_request(req, settings.jwt_secret)
    if not is_authenticated:
        return token_payload_or_error
    token_payload = token_payload_or_error
    
    # Query user.
    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])

    # Create new client.
    oauth_client = crud.oauth_client.create(db=db, owner_id=user.id)

    # Return user with token.
    return api_success({
        **serializers.oauth_client.serialize(oauth_client),
    })

@router.get("/oauth/client/expire")
async def oauth_client_expire(client_id: int, req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ OAUTH API endpoint for direct oauth authorization (Should be dissalowed by external clients). """

    # Try authenticate.
    is_authenticated, token_payload_or_error, _ = services.request.try_decode_token_from_request(req, settings.jwt_secret)
    if not is_authenticated:
        return token_payload_or_error
    token_payload = token_payload_or_error
    
    # Query user.
    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])

    # Query OAuth client.
    oauth_client = crud.oauth_client.get_by_id(db=db, client_id=client_id)

    # Verification.
    if not oauth_client:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "OAuth client not found!")
    if oauth_client.owner_id != user.id:
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "You are not owner of this OAuth client!")
    
    # Generate new OAuth token.
    crud.oauth_client.expire(db=db, client=oauth_client)

    # Return user with token.
    return api_success({
        **serializers.oauth_client.serialize(oauth_client),
    })



