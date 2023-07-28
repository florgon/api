"""
    API features schemas.
"""
from pydantic import BaseModel
from app.config import get_settings


class FeaturesModel(BaseModel):
    """
    API features response model.
    """

    auth_signup_is_open: bool
    is_under_maintenance: bool

    @classmethod
    def from_settings(cls) -> "FeaturesModel":
        settings = get_settings()
        return FeaturesModel(
            auth_signup_is_open=settings.signup_open_registration,
            is_under_maintenance=settings.service_is_under_maintenance,
        )
