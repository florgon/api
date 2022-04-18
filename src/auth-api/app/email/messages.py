"""
    Stuff for sending messages.
"""

# Libraries.
from fastapi_mail import (
    FastMail, MessageSchema
)

# Core.
from .config import config

async def send(email: str, subject: str, body: str):
    """ Sends message to single recepient email. """
    fastmail = FastMail(config)
    await fastmail.send_message(MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="plain"
    ))

async def send_verification_email(email: str, username: str, confirmation_link: str):
    """ Send verification email to user. """

    # Send email.
    await send(email, 
        "Sign-up on Florgon", 
        f"Hello, {username}! Please confirm your email address by clicking link below! Welcome to Florgon! Link: {confirmation_link}"
    )
