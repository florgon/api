"""
    Stuff for sending messages.
"""

# Libraries.
from fastapi_mail import FastMail, MessageSchema
from fastapi import BackgroundTasks

# Core.
from .config import config


async def _send_email(email: str, subject: str, body: str):
    """Sends message to single recipient email."""

    if not config:
        return  # Mail disabled.

    fastmail = FastMail(config)
    await fastmail.send_message(
        MessageSchema(subject=subject, recipients=[email], body=body, subtype="plain")
    )


async def send_verification_email(email: str, mention: str, confirmation_link: str):
    """Send verification email to user."""
    subject = "Sign-up on Florgon!"
    message = f"Hello, {mention}! Please confirm your Florgon account email address by clicking link below! Link: {confirmation_link}"
    BackgroundTasks.add_task(_send_email, email, subject, message)


async def send_verification_end_email(email: str, mention: str):
    """Send verification end email to the user."""
    subject = "Email verified on Florgon!"
    message = f"Hello, {mention}! Your Florgon account email address was verified! Welcome to Florgon!"
    BackgroundTasks.add_task(_send_email, email, subject, message)