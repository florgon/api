"""
    User schemas.
"""
from pydantic import Field, BaseModel, AnyHttpUrl


class UpdateModel(BaseModel):
    """
    update user information request model.
    """

    sex: bool | None = None
    privacy_profile_public: bool | None = None
    privacy_profile_require_auth: bool | None = None

    profile_website: AnyHttpUrl | None = None

    first_name: str | None = Field(default=None, max_length=21)
    last_name: str | None = Field(default=None, max_length=21)
    profile_bio: str | None = Field(default=None, max_length=251)
    profile_social_username_vk: str | None = Field(
        default=None, max_length=32, min_length=3
    )
    profile_social_username_tg: str | None = Field(
        default=None, max_length=32, min_length=3
    )
    profile_social_username_gh: str | None = Field(
        default=None, max_length=32, min_length=3
    )

    def get_new_fields(self, user: object):
        fields: dict[str, str | bool] = self.dict()
        return {
            field_name: field_value
            for field_name, field_value in fields.items()
            if field_value is not None
            and getattr(user, field_name, None) != field_value
        }
