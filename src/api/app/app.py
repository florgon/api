"""
    Florgon auth API server entry point.
    FastAPI server.
"""

import aioredis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .services.limiter import FastAPILimiter
from . import (
    database,
    routers,
    exception_handlers,
    config
)


# Creating application.
database.core.create_all()
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Will be refactored.
    redis = await aioredis.from_url(config.get_settings().cache_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis) 


@app.on_event("shutdown")
async def shutdown():
    # Will be refactored.
    await FastAPILimiter.close()


# Routers, handlers.
exception_handlers.register_handlers(app)
routers.register_routers(app)