"""
    User schemas.
"""
from pydantic import validator, BaseModel
from app.services.validators.user import (
    validate_profile_website_field,
    validate_profile_social_username_field,
    validate_profile_bio_field,
    validate_name_field,
)


class UpdateModel(BaseModel):
    """
    update user information request model.
    """

    sex: bool | None = None
    privacy_profile_public: bool | None = None
    privacy_profile_require_auth: bool | None = None

    first_name: str | None = None
    last_name: str | None = None
    profile_bio: str | None = None
    profile_website: str | None = None
    profile_social_username_vk: str | None = None
    profile_social_username_tg: str | None = None
    profile_social_username_gh: str | None = None

    def get_new_fields(self, user: object):
        fields: dict[str, str | bool] = self.dict()
        return {
            field_name: field_value
            for field_name, field_value in fields.items()
            if field_value is not None
            and getattr(user, field_name, None) != field_value
        }

    @validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value) -> str:
        validate_name_field(value)
        return value

    @validator("profile_bio")
    @classmethod
    def validate_profile_bio(cls, value) -> str:
        validate_profile_bio_field(value)
        return value

    @validator("profile_website")
    @classmethod
    def validate_profile_website(cls, value) -> str:
        validate_profile_website_field(value)
        return value

    @validator(
        "profile_social_username_vk",
        "profile_social_username_tg",
        "profile_social_username_gh",
    )
    @classmethod
    def validate_profile_social_usernames(cls, value) -> str:
        validate_profile_social_username_field(value)
        return value
