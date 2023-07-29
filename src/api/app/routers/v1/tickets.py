"""
    Tickets API router.
    Provides API methods for working with tickets.
"""
from fastapi.responses import JSONResponse
from fastapi import Request, Depends, APIRouter
from app.services.request.auth import try_query_auth_data_from_request
from app.services.limiter.depends import RateLimiter
from app.services.api.response import api_success
from app.serializers.ticket import serialize_ticket
from app.schemas.tickets import TicketModel
from app.database.dependencies import get_db, Session
from app.database import crud

router = APIRouter(
    include_in_schema=True,
    tags=["ticket"],
    prefix="/tickets",
    default_response_class=JSONResponse,
    dependencies=[],
)


@router.post("/", dependencies=[Depends(RateLimiter(times=2, minutes=5))])
async def create(
    model: TicketModel,
    request: Request,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Create new ticket, if authentication is passed, links with your account.
    """

    user_id: int = (
        auth_data.user.id  # type: ignore
        if (auth_data := try_query_auth_data_from_request(request, db))
        else None
    )

    return api_success(
        serialize_ticket(
            crud.ticket.create(
                db=db,
                text=model.text,
                subject=model.subject,
                first_name=model.first_name,
                last_name=model.last_name,
                middle_name=model.middle_name,
                phone_number=model.phone_number,
                email=model.email,
                user_id=user_id,
            )
        )
    )
