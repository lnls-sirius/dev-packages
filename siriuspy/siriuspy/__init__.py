from . import envars
from . import util
from . import macapp_ns
from . import macapp_ccdb
from . import macapp_web
from . import magnet
from . import naming_system
from . import namedtupple
from . import dev_types
from . import epics


import os as _os
with open(_os.path.join(__path__[0], 'VERSION'), 'r') as _f:
     __version__ = _f.read().strip()
del _os


__all__ = ['envars','util','macapp_ns','macapp_ccdb','macapp_web','magnet','naming_system',
           'namedtupple','dev_types','epics']
