import os as _os

from . import discs
from . import web
from . import util

from .magexcdat import *
del magexcdat

with open(_os.path.join(__path__[0], 'VERSION'), 'r') as _f:
    __version__ = _f.read().strip()


__all__ = ['discs','web']
