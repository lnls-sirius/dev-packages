import siriuspy.servweb as _web
import siriuspy.namesys as _namesys
import copy as _copy

_timeout = 1.0

class _TimeDevData:
    """Class with mapping of Connection among timing devices and triggers receivers.

    Data are read from the Sirius web server.
    """

    def __init__(self, timeout=_timeout):
        self._mapping = None
        self._inv_mapping = None
        if _web.server_online():
            text = _web.timing_devices_mapping(timeout=_timeout)
            self._build_mapping(text)

    def _build_mapping(self,text):
        mapping = dict()
        lines = text.splitlines()
        for n,line in enumerate(lines,1):
            line = line.strip()
            if not line or line[0] == '#': continue # empty line
            out,inn,*_ = line.split()
            out = _namesys.SiriusPVName(out)
            send = out.dev_name
            out  = out.propty.lower()
            inn = _namesys.SiriusPVName(inn)
            recv = inn.dev_name
            inn  = inn.propty.lower()
            # if (not out.endswith('out') or not out.endswith('in')) and (out[:-3] != inn[:-2]):
            #     print('Sintaxe error in timing device mapping file: line {0:d}: {1:s}'.format(n,line))
            #     return
            if send in mapping.keys():
                mapping[send].update(  { out : (recv, inn) }  )
            else:
                mapping[send] = { out : (recv, inn) }
        self._mapping = mapping

    @property
    def map(self): return _copy.deepcopy(self._mapping)

_timedata = None
def  _get_timedata():
    # encapsulating _bbbdata within a function avoid creating the global object
    # (which is time consuming) at module load time.
    global _timedata
    if _timedata is None:
        _timedata = _TimeDevData()
    return _timedata


# BBBDATA API
# ==========
def reset():
    global _timedata
    _timedata = _TimeDevData()

def server_online():
    """Return True/False if Sirius web server is online."""
    return _web.server_online()

def get_mapping():
    """Return a dictionary with the beaglebone to power supply mapping."""
    timedata =  _get_timedata()
    return timedata.map
