"""Epics-related subpackage."""
from .pv import PV
from .pv_time_serie import *
from .properties import *

# the following parameter is used to establish connections with IOC PVs.
connection_timeout = 0.050  # [s]

del pv
del properties
del pv_time_serie
