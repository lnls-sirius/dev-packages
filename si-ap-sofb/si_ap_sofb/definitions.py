import time as _time
import logging as _log
from siriuspy.envars import vaca_prefix as PREFIX
from siriuspy.util import get_last_commit_hash as _get_version

__version__ = _get_version()

WAIT_FOR_SIMULATOR = 3  # seconds
INTERVAL = 0.1
TINY_INTERVAL = 0.01
NUM_TIMEOUT = 1000

DB_FILENAME = '../pvs/ioc-si-ap-sofb-pvs.txt'
SECTION = 'SI'
PREFIX += SECTION+'-Glob:AP-SOFB:'

NR_BPMS = 160
NR_CH = 120
NR_CV = 160
NR_CORRS = NR_CH + NR_CV + 1
MTX_SZ = (2*NR_BPMS) * NR_CORRS
DANG = 2E-1  # to be used in matrix calculation
DFREQ = 200  # to be used in matrix calculation


def print_pvs_in_file(prefix, db):
    with open(DB_FILENAME, 'w') as f:
        for key in sorted(db.keys()):
            f.write(prefix + '{0:20s}\n'.format(key))
    _log.info(DB_FILENAME+' file generated with {0:d} pvs.'.format(len(db)))


def timed_out(wait_dict):
    for i in range(NUM_TIMEOUT):
        if all(wait_dict.values()):
            return False
        _time.sleep(TINY_INTERVAL)
    return True
