"""Load and process RaBPM data from static table in remote server."""

from threading import Lock as _Lock
from siriuspy.namesys import Filter as _Filter, SiriusPVName as _PVName
import siriuspy.clientweb as _web

_timeout = 1.0


class RABPMSearch:
    """Class with mapping BPMS in uTCA crates

    Data are read from the Sirius web server.
    """

    _mapping = None

    _lock = _Lock()

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
    def get_names(cls, filters=None, sorting=None):
        """Return a list with the bpm names for the given filter."""
        cls._get_data()
        return _Filter.process_filters(
            cls._names, filters=filters, sorting=sorting)

    @classmethod
    def get_slots(cls, names=None, filters=None, sorting=None):
        """Return a list with the slot of the given BPMs."""
        cls._get_data()
        if not names:
            names = cls.get_names(filters=filters, sorting=sorting)
        return [cls._mapping[k]["slot"] for k in names]

    @classmethod
    def get_crates(cls, names=None, filters=None, sorting=None):
        """Return a list with the crate of the given BPMs."""
        cls._get_data()
        if not names:
            names = cls.get_names(filters=filters, sorting=sorting)
        return [cls._mapping[k]["crate"] for k in names]

    @classmethod
    def get_pair(cls, name=None):
        """Return the pair of a given BPM name."""
        if not name:
            raise Exception('BPM name not provided!')

        slot = cls.get_slots([name])[0]
        crate = cls.get_crates([name])[0]

        doubles = [key for key, val in cls._mapping.items() if val == {
            "slot": slot, "crate": crate}]
        doubles.remove(name)
        return doubles[0]

    @classmethod
    def _get_data(cls):
        with cls._lock:
            if cls._mapping is not None:
                return
            if not _web.server_online():
                raise Exception('could not read data from web server!')
            cls._build_mapping()

    @classmethod
    def _build_mapping(cls):
        data = _web.crates_mapping(timeout=_timeout)
        mapping = dict()
        for line in data.splitlines():
            line = line.strip()
            if not line or line[0] == '#':
                continue  # empty line
            dev, slot, *_, crate = line.split()
            dev = _PVName(dev)
            if dev in mapping.keys():
                raise Exception('BPM {0:s} double entry.'.format(dev))
            crate_num = crate[-2:]
            crate_name = 'IA-20RaBPMTL' if crate_num == 21 else f'IA-{crate_num}RaBPM'
            mapping[dev] = {"slot": int(slot), "crate": crate_name}
        cls._mapping = mapping
        cls._names = sorted(cls._mapping.keys())
