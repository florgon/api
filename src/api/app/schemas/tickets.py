"""
    Ticket schemas.
"""
from pydantic import validator, BaseModel
from app.services.validators.user import (
    validate_phone_number_field,
    validate_name_field,
    validate_email_field,
    convert_email_to_standardized,
)
from app.services.api.errors import ApiErrorException, ApiErrorCode


class TicketModel(BaseModel):
    """
    Ticket request model.
    """

    text: str
    subject: str

    first_name: str
    last_name: str
    middle_name: str

    phone_number: str
    email: str

    @validator("email")
    @classmethod
    def validate_email(cls, value) -> str:
        validate_email_field(value)
        return convert_email_to_standardized(value)

    @validator("first_name", "last_name", "middle_name")
    @classmethod
    def validate_name(cls, value) -> str:
        validate_name_field(value)
        return value

    @validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value) -> str:
        validate_phone_number_field(value)
        return value

    @validator("text", "subject")
    @classmethod
    def validate_text_and_subject(cls, value) -> str:
        if len(value) < 20 or len(value) > 1000:
            raise ApiErrorException(
                ApiErrorCode.API_INVALID_REQUEST,
                "Text or subject should be longer than 19 and shorter than 1001!",
            )
        return convert_email_to_standardized(value)
