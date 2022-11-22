"""
    Stuff for sending messages.
"""

from pydantic import EmailStr
from fastapi import BackgroundTasks

# Libraries.
from fastapi_mail import MessageSchema

# Core.
from .config import fastmail
from app.config import get_logger


async def send_custom_email(emails: list[EmailStr], subject: str, body: str):
    """Sends message to email(s)."""
    if not fastmail:
        return  # Mail disabled.

    get_logger().info(
        f"Sending e-mail to {emails[0]}. '{subject}'."
        if len(emails) <= 1
        else f"Sending e-mail to {len(emails)} recepients. '{subject}'."
    )
    await fastmail.send_message(
        MessageSchema(subject=subject, recipients=emails, body=body, subtype="plain")
    )


def send_verification_email(
    background_tasks: BackgroundTasks, email: str, mention: str, confirmation_link: str
):
    """Send verification email to user."""
    subject = "Sign-up on Florgon!"
    message = f"Hello, {mention}! Please confirm your Florgon account email address by clicking link below! Link: {confirmation_link}"
    background_tasks.add_task(send_custom_email, [email], subject, message)


def send_verification_end_email(
    background_tasks: BackgroundTasks, email: str, mention: str
):
    """Send verification end email to the user."""
    subject = "Email verified on Florgon!"
    message = f"Hello, {mention}! Your Florgon account email address was verified! Welcome to Florgon!"
    background_tasks.add_task(send_custom_email, [email], subject, message)


def send_password_change_tfa_otp_email(
    background_tasks: BackgroundTasks, email: str, mention: str, otp: str
):
    """Send 2FA one time password email to the user."""
    subject = "Florgon password change!"
    message = f"Hello, {mention}! Use code below to change password for your Florgon account! Code: {otp}"
    background_tasks.add_task(send_custom_email, [email], subject, message)


def send_signin_tfa_otp_email(
    background_tasks: BackgroundTasks, email: str, mention: str, otp: str
):
    """Send 2FA one time password email for signing to the user."""
    subject = "Florgon Sign-In code!"
    message = f"Hello, {mention}! Use code below to signin in to your Florgon account! Code: {otp}"
    background_tasks.add_task(send_custom_email, [email], subject, message)
