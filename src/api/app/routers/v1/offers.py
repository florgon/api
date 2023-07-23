"""
    Offers router.
    Provides API methods (routes) for working with offers.
"""
from fastapi.responses import JSONResponse
from fastapi import Request, Depends, APIRouter
from app.services.validators.user import (
    validate_phone_number_field,
    validate_email_field,
    convert_email_to_standardized,
)
from app.services.request.auth import try_query_auth_data_from_request
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success
from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.serializers.offer import serialize_offer
from app.database.dependencies import get_db, Session
from app.database import crud
from app.config import get_settings

router = APIRouter(
    include_in_schema=True,
    tags=["offers"],
    prefix="/offer",
    default_response_class=JSONResponse,
    dependencies=[],
)


@router.get("/send")
async def send_offer(
    text: str,
    full_name: str,
    phone_number: str,
    email: str,
    request: Request,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Creates an offer in database. If auth passed, also saves user_id in offer.
    """
    if len(text) < 20 or len(text) > 1000:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "Text should be longer than 19 and shorter than 1001!",
        )
    if len(full_name) < 10 or len(full_name) > 70:
        raise ApiErrorException(
            ApiErrorCode.API_INVALID_REQUEST,
            "Full name should be longer than 9 and shorter than 71!",
        )

    validate_phone_number_field(db=db, phone_number=phone_number)
    await RateLimiter(times=2, minutes=5).check(request)
    settings = get_settings()
    validate_email_field(
        email=convert_email_to_standardized(email), db=db, settings=settings
    )
    auth_data = try_query_auth_data_from_request(req=request, db=db)
    user_id = auth_data.user.id if auth_data else None
    offer = crud.offer.create(
        db=db,
        text=text,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        user_id=user_id,  # type: ignore
    )
    return api_success(serialize_offer(offer))
