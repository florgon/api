"""
    Environment type enumeration.
"""

from enum import Enum


class Environment(Enum):
    """
    Switches behaviour of the application according to the environment.

    Development -> Usable for development process where you are not supposed to do significant internal checks.
    Production -> Usable for real deployed version, should not be used inside development environment.
    """

    development = "development"
    production = "production"
