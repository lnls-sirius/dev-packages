"""Definition module."""

import time as _time
import logging as _log
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.util import get_last_commit_hash as _get_version
import siriuspy.util as _util

__version__ = _get_version()

WAIT_FOR_SIMULATOR = 3  # seconds
INTERVAL = 0.1
TINY_INTERVAL = 0.01
NUM_TIMEOUT = 1000

SECTION = 'SI'
PREFIX = _vaca_prefix + SECTION + '-Glob:AP-SOFB:'

DANG = 2E-1  # to be used in matrix calculation
DFREQ = 200  # to be used in matrix calculation


def print_pvs_in_file(db):
    """Save pv list in file."""
    _util.save_ioc_pv_list(ioc_name='si-ap-sofb',
                           prefix=(SECTION + '-Glob:AP-SOFB:', _vaca_prefix),
                           db=db)
    _log.info('si-ap-sofb.txt file generated with {0:d} pvs.'.format(len(db)))


def timed_out(wait_dict):
    """Timed out."""
    for i in range(NUM_TIMEOUT):
        if all(wait_dict.values()):
            return False
        _time.sleep(TINY_INTERVAL)
    return True
