"""
    Florgon API email token implementation.
"""


from .base_token import BaseToken


class EmailToken(BaseToken):
    """
    Email token JWT implementation.

    Used to confirm email address.
    """

    _type = "email"

    def __init__(
        self,
        issuer: str,
        ttl: int | float,
        user_id: int,
        payload: dict | None = None,
        *,
        key: str | None = None
    ):
        super().__init__(issuer, ttl, subject=user_id, payload={}, key=key)
