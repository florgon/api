"""
    Florgon auth API server entry point.
    FastAPI server.
"""

# Libraries.
from functools import lru_cache
from os import name
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, Query
from fastapi.exceptions import RequestValidationError

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

# Configuring database.
get_db = database.dependencies.get_db
database.core.create_all()

# Creating FastAPI application.
app = FastAPI(docs_url=None, redoc_url=None)

@lru_cache()
def get_settings():
    return Settings()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exception):
    """ Custom validation exception handler. """
    return api_error(ApiErrorCode.API_INVALID_REQUEST, "Invalid request!", {
        "exc": str(exception)
    })


@app.get("/signup")
def signup(username: str, email: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    """ API endpoint to signup and create new user. """

    # Validate email.
    if crud.user.email_is_taken(db=db, email=email):
        return api_error(ApiErrorCode.AUTH_EMAIL_TAKEN, "Given email is already taken!")

    # Validate username.
    if crud.user.username_is_taken(db=db, username=username):
        return api_error(ApiErrorCode.AUTH_USERNAME_TAKEN, "Given username is already taken!")

    # Create new user.
    password = passwords.get_hashed_password(password)
    user = crud.user.create(db=db, email=email, username=username, password=password)
    token = jwt.encode(user, settings.jwt_issuer, settings.jwt_ttl, settings.jwt_secret)

    # Return user with token.
    return api_success({
        **serializers.user.serialize(user),
        "token": token
    })


@app.get("/signin")
def signin(login: str, password: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
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


@app.get("/user")
def user(token: str, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    """ Returns user information by token. """
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

@app.get("/")
def root():
    """ API index page. """
    return api_success({
        "methods": [
            "/user",
            "/signin",
            "/signup"
        ]
    })