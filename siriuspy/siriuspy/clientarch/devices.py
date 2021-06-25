"""Devices of Archive PVs."""

from copy import deepcopy as _dcopy

import numpy as _np

from ..search import BPMSearch as _BPMSearch
from ..util import ClassProperty as _classproperty

from .pvarch import PVDataSet as _PVDataSet
from .time import Time as _Time


class Orbit(_PVDataSet):
    """."""

    _CONV = 0.001  # [nm -> um]
    _BPMS_TB = None
    _BPMS_BO = None
    _BPMS_TS = None
    _BPMS_SI = None
    _PBPMS_SI = None

    class DEVICES:
        """."""

        TB_X = 'TB_X'
        TB_Y = 'TB_Y'
        BO_X = 'BO_X'
        BO_Y = 'BO_Y'
        TS_X = 'TS_X'
        TS_Y = 'TS_Y'
        SI_X = 'SI_X'
        SI_Y = 'SI_Y'
        PSI_X = 'PSI_X'
        PSI_Y = 'PSI_Y'

    Time = _Time

    @_classproperty
    def BPMS_TB(cls):
        """."""
        if cls._BPMS_TB is None:
            cls._BPMS_TB = _BPMSearch.get_names({'sec': 'TB', 'dev': 'BPM'})
        return _dcopy(cls._BPMS_TB)

    @_classproperty
    def BPMS_BO(cls):
        """."""
        if cls._BPMS_BO is None:
            cls._BPMS_BO = _BPMSearch.get_names({'sec': 'BO', 'dev': 'BPM'})
        return _dcopy(cls._BPMS_BO)

    @_classproperty
    def BPMS_TS(cls):
        """."""
        if cls._BPMS_TS is None:
            cls._BPMS_TS = _BPMSearch.get_names({'sec': 'TS', 'dev': 'BPM'})
        return _dcopy(cls._BPMS_TS)

    @_classproperty
    def BPMS_SI(cls):
        """."""
        if cls._BPMS_SI is None:
            cls._BPMS_SI = _BPMSearch.get_names({'sec': 'SI', 'dev': 'BPM'})
        return _dcopy(cls._BPMS_SI)

    @_classproperty
    def PBPMS_SI(cls):
        """."""
        if cls._PBPMS_SI is None:
            cls._PBPMS_SI = _BPMSearch.get_names({'sec': 'SI', 'dev': 'PBPM'})
        return _dcopy(cls._PBPMS_SI)

    def __init__(self, devname, connector=None):
        """."""
        self._devname = devname
        self._bpmnames, pvnames = self._get_pvnames()
        self._times = None
        self._orbits = None
        super().__init__(pvnames, connector=connector)

    @property
    def bpmnames(self):
        """Return ordered list of device BPMs."""
        return list(self._bpmnames)

    @property
    def timestamps(self):
        """Return retrieved orbit generated timestamps."""
        return self._times

    @property
    def orbits(self):
        """Return retrieved orbit interpolated values."""
        return self._orbits

    def update(self, mean_sec=None, parallel=True):
        """Update state by retrieving data."""
        super().update(mean_sec=mean_sec, parallel=parallel)

        # interpolate data
        self._times, self._orbits = self._interpolate_data(mean_sec)

    # --- private methods ---

    def _get_pvnames(self):
        if self._devname.startswith('TB'):
            bpmnames = Orbit.BPMS_TB
        elif self._devname.startswith('BO'):
            bpmnames = Orbit.BPMS_BO
        elif self._devname.startswith('TS'):
            bpmnames = Orbit.BPMS_TS
        elif self._devname.startswith('SI'):
            bpmnames = Orbit.BPMS_SI
        elif self._devname.startswith('PSI'):
            bpmnames = Orbit.PBPMS_SI
        else:
            raise ValueError('Device not defined!')
        if self._devname.endswith('X'):
            propty = ':PosX-Mon'
        elif self._devname.endswith('Y'):
            propty = ':PosY-Mon'
        else:
            raise ValueError('Device not defined!')
        pvnames = tuple(bpm + propty for bpm in bpmnames)
        return bpmnames, pvnames

    def _interpolate_data(self, mean_sec):
        # calc avg_dtime if not passed
        nr_bpms = len(self._pvdata)
        if mean_sec is None:
            mean_sec = sum(map(
                lambda p: p.timestamp[1]-p.timestamp[0],
                self._pvdata.values()))
            mean_sec /= nr_bpms

        # times vector
        t0_, t1_ = self.timestamp_start, self.timestamp_stop
        times = _np.arange(t0_, t1_, mean_sec)

        # builds orbit matrix using interpolation
        orbits = _np.zeros((len(times), nr_bpms), dtype=float)
        for i, pvname in enumerate(self._pvnames):
            pvdata = self._pvdata[pvname]
            orbits[:, i] = _np.interp(times, pvdata.timestamp, pvdata.value)
        orbits *= Orbit._CONV

        # return data
        return times, orbits

    def __getitem__(self, index):
        """Return raw timestamp and value tuple data for a given BPM."""
        if isinstance(index, int):
            pvname = self._pvnames[index]
        elif isinstance(index, str):
            if index in self._pvnames:
                pvname = index
            elif index in self._bpmnames:
                index = self._bpmnames.index(index)
                pvname = self._pvnames[index]
            else:
                raise IndexError
        pvdata = self._pvdata[pvname]
        return pvdata.timestamp, pvdata.value * Orbit._CONV
