from math import ceil
from functools import partial

from fastapi import Request, Depends, BackgroundTasks
from app.services.validators.user import (
    validate_signup_fields,
    validate_signin_fields,
    convert_email_to_standardized,
)
from app.services.tfa import validate_user_tfa_otp_from_request, generate_tfa_otp
from app.services.request.signup_host_allowance import validate_signup_host_allowance
from app.services.limiter.depends import RateLimiter
from app.services.limiter import extended_default_identifier
from app.services.api import ApiErrorException, ApiErrorCode
from app.schemas.session import SignupModel, SigninModel
from app.email import messages as email_messages
from app.database.repositories.users import UsersRepository, User
from app.database.dependencies import get_repository
from app.config import get_settings, Settings


def _tfa_limiter_callback(request, response, pexpire):
    if not get_settings().requests_limiter_enabled:
        return

    retry_after = ceil(pexpire / 1000)
    raise ApiErrorException(
        ApiErrorCode.API_TOO_MANY_REQUESTS,
        f"Too many requests! Please wait before getting new 2FA otp. Try again in {retry_after}s!",
        {"retry-after": retry_after},
        headers={"Retry-After": retry_after},
    )


async def get_valid_signin_user(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: SigninModel,
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> User:
    user = user_repo.get_user_by_login(payload.login)
    if not user and "@" in payload.login:
        user = user_repo.get_user_by_login(
            login=convert_email_to_standardized(payload.login)
        )

    user = validate_signin_fields(user=user, password=payload.password)

    if not user.security_tfa_enabled:
        return user

    if not payload.tfa_otp:
        tfa_device = "email"
        tfa_otp_is_sent = False  # If false, OTP was not sent due no need.

        if tfa_device == "email":
            # Email 2FA device.
            # Send 2FA OTP to email address.
            await RateLimiter(
                times=1,
                seconds=30,
                identifier=partial(
                    extended_default_identifier, extended_identifier="signin_email_tfa"
                ),
                callback=_tfa_limiter_callback,
            ).check(request)

            tfa_otp: str = generate_tfa_otp(user, device_type=tfa_device)  # type: ignore
            email_messages.send_signin_tfa_otp_email(
                background_tasks, user.email, user.get_mention(), tfa_otp  # type: ignore
            )
            tfa_otp_is_sent = True
        elif tfa_device == "mobile":
            # Mobile 2FA device (No need to send 2FA OTP).
            tfa_otp_is_sent = False
        else:
            raise ApiErrorException(
                ApiErrorCode.API_UNKNOWN_ERROR, "Unknown 2FA device!"
            )

        raise ApiErrorException(
            ApiErrorCode.AUTH_TFA_OTP_REQUIRED,
            "2FA authentication one time password required and was sent!",
            {"tfa_device": tfa_device, "tfa_otp_is_sent": tfa_otp_is_sent},
        )

    validate_user_tfa_otp_from_request(payload.tfa_otp, user)

    return user


async def get_valid_signup_user(
    req: Request,
    model: SignupModel,
    settings: Settings = Depends(get_settings),
    user_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> User:
    """API endpoint to signup and create new user."""

    if not settings.signup_open_registration:
        raise ApiErrorException(
            ApiErrorCode.API_FORBIDDEN,
            "Signup temporarily disabled, sorry for inconvenience...",
        )
    # Used for email where domain like `ya.ru` is same with `yandex.ru` or `yandex.com`
    email = convert_email_to_standardized(email)  # type: ignore

    validate_signup_host_allowance(db=user_repo.db, request=req)
    validate_signup_fields(user_repo.db, model)
    if not (
        user := user_repo.create(
            model.username, model.email, model.password, model.phone_number
        )
    ):
        raise ApiErrorException(
            ApiErrorCode.API_TRY_AGAIN_LATER,
            "Unable to create account at this time, please try again later.",
        )

    return user
