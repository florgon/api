"""
    Auth API auth routers.
"""

# Libraries.
from functools import lru_cache
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from validate_email import validate_email

# Database.
from app import database
from app.database import crud

# Mail.
from app import mail

# Services.
from app.services import serializers
from app.services import jwt, passwords
from app.services.api.errors import ApiErrorCode
from app.services.api.response import (
    api_error,
    api_success
)

# Other.
from app.config import Settings

# Database dependency.
get_db = database.dependencies.get_db

# Fast API router.
router = APIRouter()

@lru_cache()
def get_settings():
    return Settings()


def try_decode_token_from_request(req: Request, jwt_secret: str) -> tuple[bool, JSONResponse, str]:
    """ Tries to get and decode auth JWT token from request """
    # Get token from request.
    token = req.query_params.get("token") or req.headers.get("Authorization")
    if not token:
        return False, api_error(ApiErrorCode.AUTH_REQUIRED, "Authentication required!"), token

    # Decode token.
    try:
        token_payload = jwt.decode(token, jwt_secret)
    except jwt.jwt.exceptions.InvalidSignatureError:
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token has invalid signature!"), token
    except jwt.jwt.exceptions.ExpiredSignatureError:
        return False, api_error(ApiErrorCode.AUTH_EXPIRED_TOKEN, "Token has been expired!"), token
    except jwt.jwt.exceptions.PyJWTError:
        return False, api_error(ApiErrorCode.AUTH_INVALID_TOKEN, "Token invalid!"), token

    # All ok, return JWT payload.
    return True, token_payload, token


@router.get("/signup")
async def signup(username: str, email: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
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

    # Send email.
    await mail.send(email, "Sign-up on Florgon", "Hello, {username}! You are registered new Florgon account and used this email! Welcome to Florgon!")

    # Return user with token.
    return api_success({
        **serializers.user.serialize(user),
        "token": token
    })


@router.get("/signin")
async def signin(login: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)) -> JSONResponse:
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
async def user(req: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    """ Returns user information by token. """
    is_authenticated, token_payload_or_error, _ = try_decode_token_from_request(req, settings.jwt_secret)
    if not is_authenticated:
        return token_payload_or_error
    token_payload = token_payload_or_error

    # Query user.
    user = crud.user.get_by_id(db=db, user_id=token_payload["sub"])
    return api_success(serializers.user.serialize(user))


@router.get("/verify")
async def verify(req: Request, settings: Settings = Depends(get_settings)) -> JSONResponse:
    """ Returns is given token valid (not expired, have valid signature) or not and information about it. """
    is_authenticated, token_payload_or_error, _ = try_decode_token_from_request(req, settings.jwt_secret)
    if not is_authenticated:
        return token_payload_or_error
    token_payload = token_payload_or_error

    # All ok.
    return api_success({
        "token": {
            "subject": token_payload["sub"],
            "issuer": token_payload["iss"],
            "issued_at": token_payload["iat"],
            "expires_at": token_payload["exp"],
            "user": {
                "username": token_payload["_user"]["username"],
            }
        }
    })
