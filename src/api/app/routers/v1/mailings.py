"""
    Mailings API router.
    Provides API methods (routes) for working with admin mailing.
"""

from pydantic import EmailStr
from fastapi.responses import JSONResponse
from fastapi import Request, Depends, BackgroundTasks, APIRouter
from app.services.user_query_filter import query_users_by_filter_query
from app.services.request.auth import query_auth_data_from_request
from app.services.api.response import api_success, api_error, ApiErrorCode
from app.email.messages import send_custom_email
from app.database.dependencies import get_db, Session

router = APIRouter(include_in_schema=False)


def send_emails_for_recepients(
    background_tasks: BackgroundTasks,
    recepients: list[EmailStr],
    subject: str,
    message: str,
) -> None:
    """
    Creates tasks to send emails for users.
    """
    for recepient in recepients:
        # Bad!
        background_tasks.add_task(send_custom_email, [recepient], subject, message)


@router.get("/mailings.send")
async def method_mailings_send(
    req: Request,
    background_tasks: BackgroundTasks,
    recepient: str = "",
    subject: str = "",
    message: str = "",
    skip_create_task: bool = False,
    display_recepients: bool = False,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """Creates new mailing task (Permitted only)."""

    auth_data = query_auth_data_from_request(req, db)
    if not auth_data.user.is_admin:
        return api_error(
            ApiErrorCode.API_FORBIDDEN, "You have no access to call this method!"
        )

    if not subject or not message:
        return api_error(
            ApiErrorCode.API_INVALID_REQUEST, "Subject and message required!"
        )

    if recepient:
        recepients = [recepient]

    elif filter_query := req.query_params.get(
        "filter",
    ):
        recepients = [
            user.email for user in query_users_by_filter_query(db, filter_query)
        ]
    else:
        return api_error(ApiErrorCode.API_INVALID_REQUEST, "Filter string required!")

    if not skip_create_task:
        send_emails_for_recepients(background_tasks, recepients, subject, message)

    response = {
        "total_recepients": len(recepients),
        "task_created": not skip_create_task,
    }
    if display_recepients:
        response |= {"recepients": recepients}
    return api_success(response)
