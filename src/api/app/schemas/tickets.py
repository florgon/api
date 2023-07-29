"""
    Ticket schemas.
"""
from pydantic import validator, Field, BaseModel
from app.services.validators.user import (
    validate_phone_number_field,
    validate_email_field,
    convert_email_to_standardized,
)


class TicketModel(BaseModel):
    """
    Ticket request model.
    """

    text: str = Field(max_length=1000, min_length=20)
    subject: str = Field(max_length=1000, min_length=20)

    first_name: str = Field(max_length=21)
    last_name: str = Field(dmax_length=21)
    middle_name: str = Field(max_length=21)

    phone_number: str
    email: str

    @validator("email")
    @classmethod
    def validate_email(cls, value) -> str:
        validate_email_field(value)
        return convert_email_to_standardized(value)

    @validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value) -> str:
        validate_phone_number_field(value)
        return value
