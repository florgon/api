"""
    Auth API auth routers.
"""

# Libraries.
from functools import lru_cache
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from validate_email import validate_email

# Database.
import database
from database import crud

# Services.
from services import serializers, jwt, passwords
from services.api.errors import ApiErrorCode
from services.api.response import (
    api_error,
    api_success
)

# Other.
from config import Settings

# Database dependency.
get_db = database.dependencies.get_db

# Fast API router.
router = APIRouter(prefix="/auth")

@lru_cache()
def get_settings():
    return Settings()


@router.get("/signup")
async def signup(username: str, email: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    """ API endpoint to signup and create new user. """

    # Validate email.
    if crud.user.email_is_taken(db=db, email=email):
        return api_error(ApiErrorCode.AUTH_EMAIL_TAKEN, "Given email is already taken!")

    # Validate username.
    if crud.user.username_is_taken(db=db, username=username):
        return api_error(ApiErrorCode.AUTH_USERNAME_TAKEN, "Given username is already taken!")

    # Check email.
    if not validate_email(email, verify=False): # TODO.
        return api_error(ApiErrorCode.AUTH_EMAIL_INVALID, "Email invalid!")

    # Check username.
    if len(username) <= 4:
        return api_error(ApiErrorCode.AUTH_USERNAME_INVALID, "Username should be longer than 4!")
    if len(username) > 16:
        return api_error(ApiErrorCode.AUTH_USERNAME_INVALID, "Username should be shorten than 16!")

    # Check password.
    if len(password) <= 5:
        return api_error(ApiErrorCode.AUTH_PASSWORD_INVALID, "Password should be longer than 5!")
    if len(password) > 64:
        return api_error(ApiErrorCode.AUTH_PASSWORD_INVALID, "Password should be shorten than 64!")

    # Create new user.
    password = passwords.get_hashed_password(password)
    user = crud.user.create(db=db, email=email, username=username, password=password)
    token = jwt.encode(user, settings.jwt_issuer, settings.jwt_ttl, settings.jwt_secret)

    # Return user with token.
    return api_success({
        **serializers.user.serialize(user),
        "token": token
    })


@router.get("/signin")
async def signin(login: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    """ API endpoint to signin and get token. """

    # Query user.
    user = crud.user.get_by_username(db=db, username=login)
    if not user:
        user = crud.user.get_by_email(db=db, email=login)

    # Check credentials.
    if not user or not passwords.check_password(password=password, hashed_password=user.password):
        return api_error(ApiErrorCode.AUTH_INVALID_CREDENTIALS, "Invalid credentials")

    # Generate token.
    token = jwt.encode(user, settings.jwt_issuer, settings.jwt_ttl, settings.jwt_secret)

    # Return user with token.
    return api_success({
        **serializers.user.serialize(user),
        "token": token
    })


@router.get("/user")
async def user(req: Request, token: str | None = None, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    """ Returns user information by token. """
    token = token or req.headers.get("Authorization")
    if not token:
        return api_error(ApiErrorCode.AUTH_REQUIRED, "Authentication required!")

    try:
        token_payload = jwt.decode(token, settings.jwt_secret)
    except jwt.jwt.exceptions.InvalidSignatureError:
        return api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token has invalid signature!")
    except jwt.jwt.exceptions.ExpiredSignatureError:
        return api_error(ApiErrorCode.AUTH_EXPIRED_TOKEN, "Token has been expired!")
    except jwt.jwt.exceptions.PyJWTError:
        return api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token invalid!")

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])
    return api_success(serializers.user.serialize(user))


@router.get("/")
async def root():
    """ Auth API index page. """
    return api_success({
        "methods": [
            "/user",
            "/signin",
            "/signup"
        ]
    })