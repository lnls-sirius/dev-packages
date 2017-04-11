from . import envars
from . import util
from . import servname
from . import servccdb
from . import servweb
from . import pwrsupply
from . import magnet
from . import namesys
from . import timesys
from . import csdevice
from . import epics
from . import diagnostics

import os as _os
with open(_os.path.join(__path__[0], 'VERSION'), 'r') as _f:
     __version__ = _f.read().strip()
del _os


__all__ = ['envars', 'util', 'servname', 'servccdb', 'servweb', 'diagnostics',
           'pwrsupply', 'magnet', 'namesys', 'timesys', 'csdevice','epics']
