"""
    Stuff for sending messages.
"""

from fastapi import BackgroundTasks
# Libraries.
from fastapi_mail import MessageSchema

# Core.
from .config import fastmail


async def _send_email(email: str, subject: str, body: str):
    """Sends message to single recipient email."""
    if not fastmail:
        return  # Mail disabled.

    await fastmail.send_message(
        MessageSchema(subject=subject, recipients=[email], body=body, subtype="plain")
    )


async def send_verification_email(
    background_tasks: BackgroundTasks, email: str, mention: str, confirmation_link: str
):
    """Send verification email to user."""
    subject = "Sign-up on Florgon!"
    message = f"Hello, {mention}! Please confirm your Florgon account email address by clicking link below! Link: {confirmation_link}"
    background_tasks.add_task(_send_email, email, subject, message)


async def send_verification_end_email(
    background_tasks: BackgroundTasks, email: str, mention: str
):
    """Send verification end email to the user."""
    subject = "Email verified on Florgon!"
    message = f"Hello, {mention}! Your Florgon account email address was verified! Welcome to Florgon!"
    background_tasks.add_task(_send_email, email, subject, message)


async def send_tfa_otp_email(
    background_tasks: BackgroundTasks, email: str, mention: str, otp: str
):
    """Send 2FA one time password email to the user."""
    subject = "Florgon Sign-In code!"
    message = f"Hello, {mention}! Use code below to sign-in in to your Florgon account! Code: {otp}"
    background_tasks.add_task(_send_email, email, subject, message)
