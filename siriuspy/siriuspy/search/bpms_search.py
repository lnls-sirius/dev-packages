"""Load and process BBB to PS data from static table in remote server."""

from copy import deepcopy as _dcopy
from siriuspy.namesys import Filter as _Filter, SiriusPVName as _PVName
import siriuspy.servweb as _web

_timeout = 1.0


class BPMSearch:
    """Class with mapping BPMS.

    Data are read from the Sirius web server.
    """

    _mapping = None
    _inv_mapping = None

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
    def get_crates_mapping(cls):
        """Return a dictionary with the power supply to beaglebone mapping."""
        cls._get_data()
        return _dcopy(cls._crates_mapping)

    @classmethod
    def _get_data(cls):
        if cls._mapping is not None:
            return
        if not _web.server_online():
            raise Exception('could not read data from web server!')
        text = _web.bpms_data(timeout=_timeout)
        cls._mapping = cls._get_mapping(text)
        cls._build_crates_to_bpm_mapping()
        cls._build_data()

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

    @classmethod
    def _build_crates_to_bpm_mapping(cls):
        crates_mapping = dict()
        for k, v in cls._mapping.items():
            k2 = v['crate']
            if k2 in crates_mapping.keys():
                crates_mapping[k2] += tuple(k)
            else:
                crates_mapping[k2] = tuple(k)
        cls._crates_mapping = crates_mapping

    @classmethod
    def _build_data(cls):
        data = {k: v for k, v in cls._mapping.items() if k.sec == 'SI'}
        cls._names = sorted(data.keys())
        cls._pos = [data[k]['position'] for k in cls._names]
