"""Epics-related subpackage."""

# the following parameter is used to establish connections with IOC PVs.
CONNECTION_TIMEOUT = 0.050  # [s]
GET_TIMEOUT = 5.0  # [s]

from .pv import PV
from .pv_time_serie import *
from .properties import *
from .multiproc import CAProcessSpawn

del pv
del pv_time_serie
del properties
del multiproc
