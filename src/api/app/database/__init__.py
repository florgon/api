"""
    Database module for working with database ORM.
"""

from . import core as core
from . import dependencies as dependencies
from . import models as models
from . import crud as crud

from .dependencies import get_db as get_db
