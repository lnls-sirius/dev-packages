import os as _os
with open(_os.path.join(__path__[0], 'VERSION'), 'r') as _f:
     __version__ = _f.read().strip()
del _os


__all__ = []
