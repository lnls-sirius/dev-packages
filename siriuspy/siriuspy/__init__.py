"""Siriuspy."""

import os as _os
with open(_os.path.join(__path__[0], 'VERSION'), 'r') as _f:
    __version__ = _f.read().strip()
del _os


__all__ = [
    'callbacks', 'csdev', 'envars', 'thread', 'util',
    'bsmp', 'clientarch', 'clientconfigdb', 'clientweb', 'currinfo',
    'cycle', 'devices', 'diagbeam', 'diagsys', 'epics', 'machshift',
    'magnet', 'meas', 'namesys', 'optics', 'opticscorr', 'posang',
    'pwrsupply', 'ramp', 'search', 'simul', 'sofb', 'timesys'
    ]
