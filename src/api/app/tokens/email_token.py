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
