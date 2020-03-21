"""Epics-related subpackage."""
# the following parameter is used to establish connections with IOC PVs.
CONNECTION_TIMEOUT = 0.050  # [s]

from .pv import PV
from .pv_fake import PVFake
from .pv_time_serie import *
from .properties import *

del pv
del pv_fake
del pv_time_serie
del properties
