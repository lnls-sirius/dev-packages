"""Load and process BBB to PS data from static table in remote server."""

import os as _os
import siriuspy.servweb as _web
from siriuspy.namesys import SiriusPVName as _PVName
import copy as _copy

_timeout = 1.0

_LOCAL = _os.environ.get('CS-CONSTS-MODE', default='remote')
_bpmsdata = None


class _BPMsData:
    """Class with mapping BPMS.

    Data are read from the Sirius web server.
    """

    def __init__(self, timeout=_timeout):
        self._mapping = None
        self._inv_mapping = None
        text = ''
        if not _LOCAL.lower().startswith('remote'):
            repo = '/home/fac_files/lnls-sirius/control-system-constants/'
            with open(repo + 'diagnostics/bpms-data.txt', 'r') as f:
                text = f.read()
        else:
            if _web.server_online():
                text = _web.bpms_data(timeout=_timeout)
        self._mapping = self._get_mapping(text)
        self._build_crates_to_bpm_mapping()
        self._build_data()

    @staticmethod
    def _get_mapping(text):
        mapping = dict()
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue  # empty line
            key, pos, crate, *_ = line.split()
            key = _PVName(key)
            crate = _PVName(crate)
            if key in mapping.keys():
                raise Exception('BPM {0:s} double entry.'.format(key))
            else:
                mapping[key] = {'position': float(pos), 'crate': crate}
        return mapping

    def _build_crates_to_bpm_mapping(self):
        crates_mapping = dict()
        for k, v in self._mapping.items():
            k2 = v['crate']
            if k2 in crates_mapping.keys():
                crates_mapping[k2] += tuple(k)
            else:
                crates_mapping[k2] = tuple(k)
        self._crates_mapping = crates_mapping

    def _build_data(self):
        data = {k: v for k, v in self.map.items() if k.section == 'SI'}
        self._names = sorted(data.keys())
        self._pos = [data[k]['position'] for k in self._names]

    @property
    def map(self): return _copy.deepcopy(self._mapping)

    @property
    def names(self): return _copy.deepcopy(self._names)

    @property
    def positions(self): return _copy.deepcopy(self._pos)

    @property
    def crates_map(self): return _copy.deepcopy(self._crates_mapping)


def _get_bpmsdata():
    # encapsulating _bpmsdata within a function avoid creating a global object
    # (which is time consuming) at module load time.
    global _bpmsdata
    if _bpmsdata is None:
        _bpmsdata = _BPMsData()
    return _bpmsdata


# BPMsDATA API
# ==========
def reset():
    """Reload data from files."""
    global _bpmsdata
    _bpmsdata = _BPMsData()


def server_online():
    """Return True/False if Sirius web server is online."""
    return _web.server_online()


def get_mapping():
    """Return a dictionary with the BPMs."""
    bpmsdata = _get_bpmsdata()
    return bpmsdata.map


def get_names():
    """Return a dictionary with the."""
    bpmsdata = _get_bpmsdata()
    return bpmsdata.names


def get_positions():
    """Return a dictionary with the beaglebone to power supply mapping."""
    bpmsdata = _get_bpmsdata()
    return bpmsdata.positions


def get_crates_mapping():
    """Return a dictionary with the power supply to beaglebone mapping."""
    bpmsdata = _get_bpmsdata()
    return bpmsdata.crates_map
