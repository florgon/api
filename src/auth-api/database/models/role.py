"""
    Roles enumeration.

    I think about creating more complex roles system with database management and other stuff,
    but I don`t know how I will implement this now (I don`t know it is required or not for project).
"""

from enum import IntEnum


class Role(IntEnum):
    GUEST = 0,
    ADMIN = 1
