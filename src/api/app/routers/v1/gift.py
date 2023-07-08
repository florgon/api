"""
    Gift API router.
    Provides API methods (routes) for working gifts.
"""

from fastapi.responses import JSONResponse
from fastapi import Depends, APIRouter
from app.services.request.auth import AuthDataDependency
from app.services.limiter.depends import RateLimiter
from app.services.gift import query_and_accept_gift
from app.services.api.response import api_success
from app.database.repositories import GiftsRepository
from app.database.dependencies import get_repository

router = APIRouter(tags=["gift"])


@router.get(
    "/gift.accept",
    dependencies=[Depends(RateLimiter(times=10, minutes=5))],
)
async def method_gift_accept(
    auth_data=Depends(AuthDataDependency()),
    gifts_repo: GiftsRepository = Depends(get_repository(GiftsRepository)),
    promocode: str | None = None,
) -> JSONResponse:
    """Accepts gift."""

    query_and_accept_gift(
        gifts_repo=gifts_repo, acceptor=auth_data.user, promocode=promocode
    )
    return api_success({"gift": {"status": "accepted"}})
