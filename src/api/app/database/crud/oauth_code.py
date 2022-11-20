# pylint: disable=singleton-comparison
"""
    OAuth code CRUD utils for the database.
"""

from app.database.models.oauth_code import OAuthCode
from sqlalchemy.orm import Session


def create(db: Session, user_id: int, client_id: int, session_id: int) -> OAuthCode:
    """Creates new OAuth code object that is committed in the database already."""
    oauth_code = OAuthCode(user_id=user_id, client_id=client_id, session_id=session_id)
    db.add(oauth_code)
    db.commit()
    db.refresh(oauth_code)
    return oauth_code


def get_by_id(db: Session, code_id: int) -> OAuthCode | None:
    """Returns oauth code by id."""
    return db.query(OAuthCode).filter(OAuthCode.id == code_id).first()
