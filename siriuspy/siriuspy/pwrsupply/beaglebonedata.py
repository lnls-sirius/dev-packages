import os as _os
import siriuspy.servweb as _web
import copy as _copy

_timeout = 1.0
_bbbdata = None
_LOCAL = _os.environ.get('CS-CONSTS-MODE', default='remote')


class _BBBData:
    """Mapping of BeagleBoneBlack and the power supplies connected to them.

    Data are read from the Sirius web server.
    """

    def __init__(self, timeout=_timeout):
        self._mapping = None
        self._inv_mapping = None
        if not _LOCAL.lower().startswith('remote'):
            with open('/home/fac_files/lnls-sirius/' +
                      'control-system-constants/' +
                      'pwrsupply/beaglebone-mapping.txt', 'r') as f:
                text = f.read()
        else:
            if _web.server_online():
                text = _web.beaglebone_power_supplies_mapping(timeout=_timeout)
        self._mapping = self._get_mapping(text)
        self._build_inv_mapping()

    @staticmethod
    def _get_mapping(text):
        mapping = dict()
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue  # empty line
            key, *val = line.split()
            if key in mapping.keys():
                mapping[key] += tuple(val)
            else:
                mapping[key] = tuple(val)
        return mapping

    def _build_inv_mapping(self):
        inv_mapping = dict()
        for k, vs in self._mapping.items():
            for v in vs:
                inv_mapping[v] = k
        self._inv_mapping = inv_mapping

    @property
    def map(self): return _copy.deepcopy(self._mapping)

    @property
    def inverse_map(self): return _copy.deepcopy(self._inv_mapping)


def _get_bbbdata():
    # encapsulating _bbbdata within a function avoid creating the global object
    # (which is time consuming) at module load time.
    global _bbbdata
    if _bbbdata is None:
        _bbbdata = _BBBData()
    return _bbbdata


# BBBDATA API
# ==========
def reset():
    """Reload data."""
    global _bbbdata
    _bbbdata = _BBBData()


def server_online():
    """Return True/False if Sirius web server is online."""
    return _web.server_online()


def get_mapping():
    """Return a dictionary with the beaglebone to power supply mapping."""
    bbbdata = _get_bbbdata()
    return bbbdata.map


def get_inverse_mapping():
    """Return a dictionary with the power supply to beaglebone mapping."""
    bbbdata = _get_bbbdata()
    return bbbdata.inverse_map
