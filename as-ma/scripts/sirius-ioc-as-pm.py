#!/usr/local/bin/python-sirius -u
"""AS PM IOC executable."""

import os
from as_ma import as_ma as ioc_module


# NOTE: maximum epics array size
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '100000'


ioc_module.run('as-pm')
