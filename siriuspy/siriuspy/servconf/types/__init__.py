"""Types subpackage."""

import pkgutil as _pkgutil
from siriuspy.csdevice.pwrsupply import default_wfmsize as \
    _default_wfmsize

_ctypes = []
for loader, module_name, is_pkg in _pkgutil.walk_packages(__path__):
    _ctypes.append(module_name)
    module = loader.find_module(module_name).load_module(module_name)
    exec('%s = module' % module_name)


_ref_wfm_array = [0.0 for _ in range(_default_wfmsize)]
