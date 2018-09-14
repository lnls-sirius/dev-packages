"""Epics-related subpackage."""
from .pv import *
from .pv_time_serie import *
from .properties import *
from .pwrsupply import *

# the following parameter is used to establish connections with IOC PVs.
connection_timeout = 0.050  # [s]

del pwrsupply
del properties
del pv_time_serie
del pv
