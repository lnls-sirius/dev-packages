from . import config
from . import util
from . import ns
from . import ccdb
from . import web
from . import magnet

import os as _os
with open(_os.path.join(__path__[0], 'VERSION'), 'r') as _f:
     __version__ = _f.read().strip()
del _os

__all__ = ['config','util','ns','ccdb','web','magnet']
