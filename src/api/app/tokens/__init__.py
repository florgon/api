"""
    Florgon API tokens.

    Provides class interfaces for working with tokens (access / session / etc).
    Provides base class `base_token.BaseToken` for implementation of own token type.
    All tokens should be child classes of BaseToken class.
"""

from . import access_token
from . import session_token
from . import email_token
from . import oauth_code
