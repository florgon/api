"""
    Mailings API router.
    Provides API methods (routes) for working with admin mailing.
"""

from datetime import datetime
from app.services.api.response import api_error, ApiErrorCode, api_success
from app.services.request.auth import query_auth_data_from_request
from app.database.dependencies import get_db, Session
from app.database.models.user import User
from app.database import crud
from app.email.messages import send_custom_email
from fastapi import APIRouter, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse


router = APIRouter()


SECONDS_IN_WEEK = 7 * 24 * 60 * 60
QUERY_FILTER_SEPARATOR = ";"
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


def query_users_by_filter_query(db: Session, filter_query: str) -> list[User]:
    """
    Returns list of users from database filtere by string query filter.
    """
    query_params = filter_query.split(QUERY_FILTER_SEPARATOR)
    query_params = list(filter(lambda fp: fp in QUERY_FILTER_PARAMS, query_params))
    # Doing database requests like that is not good!
    # later, that will be reworked.
    users = crud.user.get_all(db)

    # Apply filters for users list.
    for query_param in query_params:
        query_filter_func = QUERY_FILTER_PARAMS[query_param]
        users = filter(query_filter_func, users)  # Chaining.
    return list(users)


def send_emails_for_users(
    background_tasks: BackgroundTasks, users: list[User], subject: str, message: str
) -> None:
    """
    Creates tasks to send emails for users.
    """
    recepients = [user.email for user in users]
    for recepient in recepients:
        # Bad!
        background_tasks.add_task(send_custom_email, [recepient], subject, message)


@router.get("/mailings.send")
async def method_mailings_send(
    req: Request,
    background_tasks: BackgroundTasks,
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

    filter_query = req.query_params.get(
        "filter",
    )
    if not filter_query:
        return api_error(ApiErrorCode.API_INVALID_REQUEST, "Filter string required!")

    users = query_users_by_filter_query(db, filter_query)
    if not skip_create_task:
        send_emails_for_users(background_tasks, users, subject, message)

    response = {
        "total_recepients": len(users),
        "task_created": not skip_create_task,
    }
    if display_recepients:
        response |= {"recepients": users}
    return api_success(response)
