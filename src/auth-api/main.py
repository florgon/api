"""
    Florgon auth API server entry point.
    FastAPI server.
"""

# Libraries.
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Database.
import database
from database import crud

from services import serializers
from services.api.errors import ApiErrorCode
from services.api.response import (
    api_error,
    api_success
)


# Configuring database.
get_db = database.dependencies.get_db
database.core.create_all()

# Creating FastAPI application.
app = FastAPI(docs_url=None, redoc_url=None)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exception):
    """ Custom validation exception handler. """
    return api_error(ApiErrorCode.API_INVALID_REQUEST, "Invalid request!", {
        "exc": str(exception)
    })


@app.get("/signup")
def signup(username: str, email: str, password: str, db: Session = Depends(get_db)):
    """ API endpoint to signup and create new user. """
    user = crud.user.create(db=db, email=email, username=username, password=password)
    return api_success(serializers.user.serialize(user))

@app.get("/user")
def user(db: Session = Depends(get_db)):
    user = crud.user.get_by_id(db=db, user_id=0)
    return api_success(serializers.user.serialize(user))