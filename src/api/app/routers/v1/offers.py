
"""
    Offers router.
    Provides API methods (routes) for working with offers.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.database.dependencies import Session, get_db
from app.database import crud
from app.services.request.auth import try_query_auth_data_from_request
from app.services.api.errors import ApiErrorException, ApiErrorCode
from app.serializers.offer import serialize_offer
from app.config import get_settings
from app.services.validators.user import (
    validate_phone_number_field,
    validate_email_field,
    convert_email_to_standardized,
)

router = APIRouter(tags=["offers"])


@router.get("/offers.send")
async def method_offer_send(
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
    settings = get_settings()
    validate_email_field(email=convert_email_to_standardized(email), db=db, settings=settings)
    authorized, auth_data = try_query_auth_data_from_request(req=request, db=db)
    user_id = auth_data.user_id if authorized else None
    offer = crud.offer.create(
        db=db,
        text=text,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        user_id=user_id,
    )
    return serialize_offer(offer)
