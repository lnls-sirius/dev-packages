"""Epics-related subpackage."""
from .pv import *
from .pvsset import *
from .pv_time_serie import *
from .pwrsupply import *

# the following parameter is used to establish connections with IOC PVs.
connection_timeout = 0.050  # [s]

del pwrsupply
del pv_time_serie
del pvsset
del pv
