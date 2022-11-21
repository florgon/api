"""
    Mailings API router.
    Provides API methods (routes) for working with admin mailing.
"""

from datetime import datetime
from app.services.api.response import api_error, ApiErrorCode, api_success
from app.services.request.auth import query_auth_data_from_request
from app.database.dependencies import get_db, Session
from app.database import crud
from app.email.messages import send_custom_email
from fastapi import APIRouter, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse


router = APIRouter()


SECONDS_IN_WEEK = 7 * 24 * 60 * 60
QUERY_FILTER_PARAMS = {
    "admin": lambda _, u: u.is_admin,
    "has_oauth_clients": lambda db, u: len(crud.oauth_client.get_by_owner_id(db, u.id))
    > 0,
    "female": lambda _, u: u.is_female(),
    "male": lambda _, u: not u.is_female(),
    "active": lambda _, u: u.is_active,
    "inactive": lambda _, u: not u.is_active,
    "verified": lambda _, u: u.is_verified,
    "unverified": lambda _, u: not u.is_verified,
    "not_admin": lambda _, u: not u.is_admin,
    "vip": lambda _, u: u.is_vip,
    "not_vip": lambda _, u: not u.is_vip,
    "tfa_enabled": lambda _, u: u.security_tfa_enabled,
    "signup_last_week": lambda _, u: (u.time_created - datetime.now()).seconds
    > SECONDS_IN_WEEK,
    "online_last_week": lambda _, u: (u.time_online - datetime.now()).seconds
    > SECONDS_IN_WEEK,
}


@router.get("/mailings.send")
async def method_mailings_send(
    req: Request,
    background_tasks: BackgroundTasks,
    filter: str = "",
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

    if not filter:
        return api_error(ApiErrorCode.API_INVALID_REQUEST, "Filter string required!")

    filter_param_allowed_names = QUERY_FILTER_PARAMS.keys()
    filter_params = list(
        filter(lambda fp: fp in filter_param_allowed_names, filter.split(";"))
    )

    # Doing database requests like that is not good!
    # later, that will be reworked.
    users = crud.user.get_all(db)
    for filter_param in filter_params:
        users = filter(
            QUERY_FILTER_PARAMS[filter_param],
            users,
        )
    users = list(users)
    recepients = [user.email for user in users]

    if not skip_create_task:
        for recepient in recepients:
            # Bad!
            background_tasks.add_task(send_custom_email, [recepient], subject, message)

    response = {
        "total_recepients": len(recepients),
        "task_created": not skip_create_task,
    }
    if display_recepients:
        response |= {"recepients": recepients}
    return api_success(response)
