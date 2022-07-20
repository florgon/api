"""
    Stuff for sending messages.
"""

# Libraries.
from fastapi_mail import FastMail, MessageSchema

# Core.
from .config import config


async def send(email: str, subject: str, body: str):
    """Sends message to single recipient email."""

    if not config:
        return  # Mail disabled.

    fastmail = FastMail(config)
    await fastmail.send_message(
        MessageSchema(subject=subject, recipients=[email], body=body, subtype="plain")
    )


async def send_verification_email(email: str, username: str, confirmation_link: str):
    """Send verification email to user."""

    # Send email.
    await send(
        email,
        "Sign-up on Florgon",
        f"Hello, {username}! Please confirm your Florgon account email address by clicking link below! "
        f"Welcome to Florgon! "
        f"Link: {confirmation_link}",
    )


async def send_verification_end_email(email: str, username: str):
    """Send verification end email to user."""

    # Send email.
    await send(
        email,
        "Email verified on Florgon!",
        f"Hello, {username}! Your Florgon account email address was verified!"
        f"Welcome to Florgon! ",
    )
