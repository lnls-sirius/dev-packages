"""Load and process BBB to PS data from static table in remote server."""

from copy import deepcopy as _dcopy
from threading import Lock as _Lock
from siriuspy.namesys import Filter as _Filter, SiriusPVName as _PVName
import siriuspy.clientweb as _web

_timeout = 1.0


class BPMSearch:
    """Class with mapping BPMS.

    Data are read from the Sirius web server.
    """

    _mapping = None

    _lock = _Lock()

    # BPMsDATA API
    # ==========
    @classmethod
    def reset(cls):
        """Reload data from files."""
        cls._mapping = None
        cls._get_data()

    @classmethod
    def server_online(cls):
        """Return True/False if Sirius web server is online."""
        return _web.server_online()

    @classmethod
    def is_valid_devname(cls, devname):
        """Check if devname is a valid BPM or PBPM name."""
        cls._get_data()
        return devname in cls._mapping

    @classmethod
    def is_photon_bpm(cls, devname):
        """Check whether BPM is a Phothon BPM (XBPM)."""
        devname = _PVName(devname)
        return devname.dev == 'PBPM'

    @classmethod
    def is_rf_bpm(cls, devname):
        """Check whether BPM is a RF BPM."""
        devname = _PVName(devname)
        return devname.dev == 'BPM'

    @classmethod
    def is_id_rf_bpm(cls, devname):
        """Check whether BPM is from Insertion Device."""
        devname = _PVName(devname)
        return devname.sub.endswith('SA', 'SB', 'SP')

    @classmethod
    def get_mapping(cls):
        """Return a dictionary with the BPMs."""
        cls._get_data()
        return _dcopy(cls._mapping)

    @classmethod
    def get_names(cls, filters=None, sorting=None):
        """Return a list with the bpm names for the given filter."""
        cls._get_data()
        return _Filter.process_filters(
            cls._names, filters=filters, sorting=sorting)

    @classmethod
    def get_nicknames(cls, names=None, filters=None, sorting=None):
        """Return a list with BPM nicknames."""
        cls._get_data()
        if not names:
            names = cls.get_names(filters=filters, sorting=sorting)
        nicknames = len(names)*['']
        for i, bpm in enumerate(names):
            nicknames[i] = bpm.sub + ('-' + bpm.idx if bpm.idx else '')
        return nicknames

    @classmethod
    def get_positions(cls, names=None, filters=None, sorting=None):
        """Return a list with the positions along the ring."""
        cls._get_data()
        if not names:
            names = cls.get_names(filters=filters, sorting=sorting)
        return [cls._mapping[k]['position'] for k in names]

    @classmethod
    def _get_data(cls):
        with cls._lock:
            if cls._mapping is not None:
                return
            if not _web.server_online():
                raise Exception('could not read data from web server!')
            text = _web.bpms_data(timeout=_timeout)
            cls._build_mapping(text)

    @classmethod
    def _build_mapping(cls, text):
        mapping = dict()
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line[0] == '#':
                continue  # empty line
            key, pos, *_ = line.split()
            key = _PVName(key)
            if key in mapping.keys():
                raise Exception('BPM {0:s} double entry.'.format(key))
            else:
                mapping[key] = {'position': float(pos)}
        cls._mapping = mapping
        cls._names = sorted(cls._mapping.keys())
