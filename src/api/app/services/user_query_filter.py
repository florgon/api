"""
    Filters users by query filter.
"""

from functools import partial
from datetime import datetime

from app.database.models.user import User
from app.database.dependencies import Session
from app.database import crud


def _qfp_signup_last_week(_, u: User) -> bool:
    if u.time_online is None:
        return False
    return (datetime.now() - u.time_created).seconds > SECONDS_IN_WEEK


def _qfp_online_last_week(_, u: User) -> bool:
    if u.time_online is None:
        return False
    return (datetime.now() - u.time_online).seconds > SECONDS_IN_WEEK


def _qfp_has_oauth_clients(db: Session, u: User) -> bool:
    return len(crud.oauth_client.get_by_owner_id(db, u.id)) > 0


SECONDS_IN_WEEK = 7 * 24 * 60 * 60
QUERY_FILTER_SEPARATOR = ";"
QUERY_FILTER_PARAMS = {
    "all": lambda *_: True,
    "admin": lambda _, u: u.is_admin,
    "has_oauth_clients": _qfp_has_oauth_clients,
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
    "signup_last_week": _qfp_signup_last_week,
    "online_last_week": _qfp_online_last_week,
}


def query_users_by_filter_query(db: Session, filter_query: str) -> list[User]:
    """
    Returns list of users from database filter by string query filter.
    """
    query_params = filter_query.split(QUERY_FILTER_SEPARATOR)
    query_params = list(filter(lambda fp: fp in QUERY_FILTER_PARAMS, query_params))
    # Doing database requests like that is not good!
    # later, that will be reworked.
    users = crud.user.get_all(db)

    # Apply filters for users list.
    for query_param in query_params:
        query_filter_func = QUERY_FILTER_PARAMS[query_param]
        users = filter(partial(query_filter_func, db), users)  # Chaining.
    return list(users)
