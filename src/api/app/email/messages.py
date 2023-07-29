"""
    Stuff for sending messages.
    
    TODO: Allow subtype to be different.
    TODO: Allow template engine.
    
    !TODO: Refactor message wrappers (senders) and replace with engine.
"""

from fastapi_mail.errors import ConnectionErrors
from fastapi_mail import MessageType, MessageSchema
from fastapi import BackgroundTasks
from app.services.verification import generate_confirmation_link
from app.database.models.user import User
from app.config import get_logger

from .config import provider


async def send_custom_email(recepients: list[str], subject: str, body: str) -> None:
    """
    Simple wrapper around provider messaging.
    """
    if not provider:
        return

    recepients_count = len(recepients)
    get_logger().info(
        f"[email] Sending mail to {recepients[0]} with subject '{subject}'."
        if recepients_count == 1
        else f"[email] Sending mail to {recepients_count} recepients with subject '{subject}'."
    )

    schema = MessageSchema(
        subject=subject, recipients=recepients, body=body, subtype=MessageType.plain
    )
    try:
        await provider.send_message(schema)
    except ConnectionErrors as e:
        get_logger().error(f"[email] Failed to send message! Error: {e}")


def send_verification_email(background_tasks: BackgroundTasks, user: User):
    """Send verification email to user."""
    subject = "Sign-up on Florgon!"
    message = f"Hello, {user.get_mention()}! Please confirm your Florgon account email address by clicking link below! Link: {generate_confirmation_link(user.id)}"  # type: ignore
    background_tasks.add_task(send_custom_email, [user.email], subject, message)  # type: ignore


def send_verification_end_email(background_tasks: BackgroundTasks, user: User):
    """Send verification end email to the user."""
    subject = "Email verified on Florgon!"
    message = f"Hello, {user.get_mention()}! Your Florgon account email address was verified! Welcome to Florgon!"
    background_tasks.add_task(send_custom_email, [user.email], subject, message)  # type: ignore


def send_password_change_tfa_otp_email(
    background_tasks: BackgroundTasks, email: str, mention: str, otp: str
):
    """Send 2FA one time password change email to the user."""
    subject = "Florgon password change!"
    message = f"Hello, {mention}! Use code below to change password for your Florgon account! Code: {otp}"
    background_tasks.add_task(send_custom_email, [email], subject, message)


def send_password_changed_notification_email(
    background_tasks: BackgroundTasks, email: str, mention: str
):
    """Send notification that there was change of the password!"""
    subject = "Florgon password was changed!"
    message = f"Hello, {mention}! Your password has been changed or reseted! If you are not changed or reseted your password, please contact support@florgon.com!"
    background_tasks.add_task(send_custom_email, [email], subject, message)


def send_password_reset_email(
    background_tasks: BackgroundTasks, email: str, mention: str, otp: str
):
    """Send 2FA one time password reset email to the user."""
    subject = "Florgon password reset!"
    message = f"Hello, {mention}! Use code below to reset password for your Florgon account! Code: {otp}. If you are not requested to reset your password, please contact support@florgon.com!"
    background_tasks.add_task(send_custom_email, [email], subject, message)


def send_signin_tfa_otp_email(
    background_tasks: BackgroundTasks, email: str, mention: str, otp: str
):
    """Send 2FA one time password email for signing to the user."""
    subject = "Florgon Sign-In code!"
    message = f"Hello, {mention}! Use code below to signin in to your Florgon account! Code: {otp}"
    background_tasks.add_task(send_custom_email, [email], subject, message)
