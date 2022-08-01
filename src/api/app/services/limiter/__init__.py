"""
    NOTICE FROM FLORGON.
    This code is licensed to LICENSE file.
    And this code is NOT A PART of Florgon code base.
    https://github.com/long2ice/fastapi-limiter/blob/master/LICENSE

    (Why: Original has fatal error which is updated in repo, but not being pushed to pypi)
"""


from math import ceil
from typing import Callable

import aioredis
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from app.config import get_settings


async def default_identifier(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    else:
        ip = request.client.host
    return ip + ":" + request.scope["path"]


async def default_callback(
    request: Request, response: Response | None, pexpire: int
):  # pylint: disable=unused-argument
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    if not get_settings().requests_limiter_enabled:
        return

    expire = ceil(pexpire / 1000)
    raise HTTPException(
        HTTP_429_TOO_MANY_REQUESTS,
        "Too Many Requests",
        headers={"Retry-After": str(expire)},
    )


class FastAPILimiter:
    redis: aioredis.Redis = None
    prefix: str = None
    lua_sha: str = None
    identifier: Callable = None
    callback: Callable = None
    lua_script = """local key = KEYS[1]
local limit = tonumber(ARGV[1])
local expire_time = ARGV[2]
local current = tonumber(redis.call('get', key) or "0")
if current > 0 then
 if current + 1 > limit then
 return redis.call("PTTL",key)
 else
        redis.call("INCR", key)
 return 0
 end
else
    redis.call("SET", key, 1,"px",expire_time)
 return 0
end"""

    @classmethod
    async def init(
        cls,
        redis: aioredis.Redis,
        prefix: str = "fastapi-limiter",
        identifier: Callable = default_identifier,
        callback: Callable = default_callback,
    ):
        cls.redis = redis
        cls.prefix = prefix
        cls.identifier = identifier
        cls.callback = callback
        cls.lua_sha = await redis.script_load(cls.lua_script)

    @classmethod
    async def close(cls):
        await cls.redis.close()


async def on_startup():
    settings = get_settings()
    redis = await aioredis.from_url(
        settings.cache_dsn, encoding=settings.cache_encoding, decode_responses=True
    )

    await FastAPILimiter.init(redis)


async def on_shutdown():
    await FastAPILimiter.close()
