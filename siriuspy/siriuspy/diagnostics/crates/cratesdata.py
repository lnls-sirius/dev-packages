import siriuspy.servweb as _web
import copy as _copy

_timeout = 1.0
_LOCAL = True

class _CratesData:
    """Class with mapping of BeagleBoneBlack and the power supplies connected to them.

    Data are read from the Sirius web server.
    """

    def __init__(self, timeout=_timeout):
        self._mapping = None
        self._inv_mapping = None
        if _web.server_online():
            if _LOCAL:
                with open('/home/fac_files/lnls-sirius/control-system-constants/'+
                          'diagnostics/crates-connection.txt','r') as f:
                    text = f.read()
            else:
                text = _web.crate_to_bpm_mapping(timeout=_timeout)
            self._mapping = self._get_mapping(text)
            self._build_inv_mapping()

    @staticmethod
    def _get_mapping(text):
        mapping = dict()
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#': continue # empty line
            key,*val = line.split()
            if key in mapping.keys():
                mapping[key] += tuple(val)
            else:
                mapping[key] = tuple(val)
        return mapping

    def _build_inv_mapping(self):
        inv_mapping = dict()
        for k,vs in self._mapping.items():
            for v in vs: inv_mapping[v] = k
        self._inv_mapping = inv_mapping

    @property
    def map(self): return _copy.deepcopy(self._mapping)

    @property
    def inverse_map(self): return _copy.deepcopy(self._inv_mapping)

_cratesdata = None
def  _get_cratesdata():
    # encapsulating _cratesdata within a function avoid creating the global object
    # (which is time consuming) at module load time.
    global _cratesdata
    if _cratesdata is None:
        _cratesdata = _CratesData()
    return _cratesdata


# CratesDATA API
# ==========
def reset():
    global _cratesdata
    _cratesdata = _CratesData()

def server_online():
    """Return True/False if Sirius web server is online."""
    return _web.server_online()

def get_mapping():
    """Return a dictionary with the beaglebone to power supply mapping."""
    cratesdata =  _get_cratesdata()
    return cratesdata.map

def get_inverse_mapping():
    """Return a dictionary with the power supply to beaglebone mapping."""
    cratesdata =  _get_cratesdata()
    return cratesdata.inverse_map
