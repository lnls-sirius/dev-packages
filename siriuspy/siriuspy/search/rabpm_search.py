"""Load and process RaBPM data from static table in remote server."""

from threading import Lock as _Lock
from siriuspy.namesys import Filter as _Filter, SiriusPVName as _PVName
import siriuspy.clientweb as _web

_timeout = 1.0


class RaBPMSearch:
    """Class with mapping devices in uTCA crates.

    Data are read from the Control System Constants Server.
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
    def get_names(cls, filters=None):
        """Return a list with the device names for the given filter.

        Parameters
        ----------
        filters : Filter object, optional
            Filter select a subset of devices.
        """
        cls._get_data()
        return _Filter.process_filters(cls._names, filters=filters)

    @classmethod
    def get_slots(cls, names=None, filters=None):
        """Return a list with the slots of the given devices.

        Parameters
        ----------
        names : string list, optional
            Desired device name.
        filters : Filter object, optional
            Filter select a subset of devices.
        """
        cls._get_data()
        if not names:
            names = cls.get_names(filters=filters)
        return [cls._mapping[k]["slot"] for k in names]

    @classmethod
    def get_crate_names(cls, names=None, filters=None):
        """Return a list with the crate names of the given devices.

        Parameters
        ----------
        names : string list, optional
            Desired device name.
        filters : Filter object, optional
            Filter select a subset of devices.
        """
        cls._get_data()
        if not names:
            names = cls.get_names(filters=filters)
        return [cls._mapping[k]["crate_name"] for k in names]

    @classmethod
    def get_crate_numbers(cls, names=None, filters=None):
        """Return a list with the crate numbers of the given devices.

        Parameters
        ----------
        names : string list, optional
            Desired device name.
        filters : Filter object, optional
            Filter select a subset of devices.
        """
        cls._get_data()
        if not names:
            names = cls.get_names(filters=filters)
        return [cls._mapping[k]["crate_number"] for k in names]

    @classmethod
    def conv_devname_2_slot(cls, name):
        """Return the slot of the given device name.

        Parameters
        ----------
        names : string
            Desired device name.
        """
        cls._get_data()
        return cls._mapping[name]["slot"]

    @classmethod
    def conv_devname_2_cratename(cls, name):
        """Return the crate name of the given device name.

        Parameters
        ----------
        names : string
            Desired device name.
        """
        cls._get_data()
        return cls._mapping[name]["crate_name"]

    @classmethod
    def conv_devname_2_cratenumber(cls, name):
        """Return the crate number of the given device name.

        Parameters
        ----------
        names : string
            Desired device name.
        """
        cls._get_data()
        return cls._mapping[name]["crate_number"]

    @classmethod
    def get_bpm_pair(cls, name):
        """ Each BPM share its slot with another BPM, defining a BPM pair.
        Return the pair of a given BPM name.

        Parameters
        ----------
        names : string
            Desired device name.
        """

        slot = cls.conv_devname_2_slot(name)
        cratename = cls.conv_devname_2_cratename(name)

        target = {"slot": slot, "crate_name": cratename}

        doubles = [key for key, val in cls._mapping.items() if
                   (val.get("slot") == target.get("slot") and val.get("crate_name") == target.get("crate_name"))]

        doubles.remove(name)
        if (len(doubles) != 1):
            print("Device does not have a pair.")
            return

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
            crate_name = ('IA-20RaBPMTL' if int(crate_num) == 21 else
                          f'IA-{crate_num}RaBPM')
            mapping[dev] = {
                "slot": int(slot),
                "crate_name": crate_name,
                "crate_number": int(crate_num)}
        cls._mapping = mapping
        cls._names = sorted(cls._mapping.keys())
