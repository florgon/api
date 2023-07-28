"""
    Session schemas.
"""
from pydantic import BaseModel


class SigninModel(BaseModel):
    """
    Sign-in (login) request model.
    """

    login: str
    password: str
    tfa_otp: str = ""


class SignupModel(BaseModel):
    """
    Sign-up (register) request model.
    """

    username: str
    email: str
    password: str
    phone_number: str = ""


class AuthModel(BaseModel):
    """
    Session authentication response model.
    """

    session_token: str
    sid: int


class LogoutModel(BaseModel):
    """
    Logout request model.
    """

    revoke_all: bool = False  # Revoke all active sessions.
    exclude_current: bool = False  # Exclude current session from active sessions.
    session_id: int | None = None  # Logout specified session by id.
