"""
    Florgon auth API server entry point.
    FastAPI server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import (
    database,
    routers,
    exception_handlers
)


# Creating application.
database.core.create_all()
app = FastAPI(docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers, handlers.
exception_handlers.register_handlers(app)
routers.register_routers(app)