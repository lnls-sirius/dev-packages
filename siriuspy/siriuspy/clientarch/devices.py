"""Devices of Archive PVs."""

from copy import deepcopy as _dcopy

import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from ..search import BPMSearch as _BPMSearch, PSSearch as _PSSearch

from .pvarch import PVDataSet as _PVDataSet
from .time import Time as _Time


class BaseDevice(_PVDataSet):
    """."""

    _CONV = 0.001

    DEVICES = _get_namedtuple('Devices', ('a', ))
    PROPTIES = _get_namedtuple('Propties', ('a', ))

    Time = _Time

    def __init__(self, devname, propty='', connector=None):
        """."""
        if devname in self.DEVICES:
            self._devname = self.DEVICES._fields[devname]
        elif devname in self.DEVICES._fields:
            self._devname = devname
        else:
            ValueError('Wrong value for devname')
        if propty in self.PROPTIES:
            self._propty = propty
        elif propty in self.PROPTIES._fields:
            idx = self.PROPTIES._fields.index(propty)
            self._propty = self.PROPTIES[idx]
        else:
            ValueError('Wrong value for propty')
        self._devnames, pvnames = self._get_pvnames()
        self._times = None
        self._values = None
        super().__init__(pvnames, connector=connector)
        self._parallel_query_bin_interval = 3600

    @property
    def devnames(self):
        """Return ordered list of device names."""
        return _dcopy(self._devnames)

    @property
    def timestamps(self):
        """Return retrieved orbit generated timestamps."""
        return self._times

    @property
    def values(self):
        """Return retrieved orbit interpolated values."""
        return self._values

    def update(self, mean_sec=None, parallel=True):
        """Update state by retrieving data."""
        super().update(mean_sec=mean_sec, parallel=parallel)

        # interpolate data
        self._times, self._values = self._interpolate_data(mean_sec)

    # --- private methods ---

    def _get_pvnames(self):
        devnames = []
        pvnames = []
        return devnames, pvnames

    def _interpolate_data(self, mean_sec):
        # calc mean_sec if not passed
        nr_pvs = len(self._pvdata)
        if mean_sec is None:
            mean_sec = sum(map(
                lambda p: p.timestamp[1]-p.timestamp[0],
                self._pvdata.values()))
            mean_sec /= nr_pvs

        # times vector
        t0_, t1_ = self.timestamp_start, self.timestamp_stop
        times = _np.arange(t0_, t1_, mean_sec)

        # builds orbit matrix using interpolation
        values = _np.zeros((len(times), nr_pvs), dtype=float)
        for i, pvname in enumerate(self._pvnames):
            pvdata = self._pvdata[pvname]
            values[:, i] = _np.interp(times, pvdata.timestamp, pvdata.value)
        values *= Orbit._CONV

        # return data
        return times, values

    def __getitem__(self, index):
        """Return raw timestamp and value tuple data for a given BPM."""
        if isinstance(index, int):
            pvname = self._pvnames[index]
        elif isinstance(index, str):
            if index in self._pvnames:
                pvname = index
            elif index in self._devnames:
                index = self._devnames.index(index)
                pvname = self._pvnames[index]
            else:
                raise IndexError
        pvdata = self._pvdata[pvname]
        return pvdata.timestamp, pvdata.value * Orbit._CONV


class Orbit(BaseDevice):
    """."""

    _CONV = 0.001  # [nm -> um]

    DEVICES = _get_namedtuple(
        'Devices', ('TB_BPM', 'TS_BPM', 'BO_BPM', 'SI_BPM', 'SI_PBPM'))
    PROPTIES = _get_namedtuple(
        'Propties',
        ('PosX', 'PosY', 'PosQ', 'Sum'),
        ('PosX-Mon', 'PosY-Mon', 'PosQ-Mon', 'Sum-Mon'))

    def __init__(self, devname='SI_BPM', propty='PosX-Mon', connector=None):
        """."""
        super().__init__(devname, propty=propty, connector=connector)

    # --- private methods ---
    def _get_pvnames(self):
        sec, dev = self._devname.split('_')
        devnames = _dcopy(_BPMSearch.get_names({'sec': sec, 'dev': dev}))
        pvnames = tuple(dev+':'+self._propty for dev in devnames)
        return devnames, pvnames


class Correctors(BaseDevice):
    """."""

    _CONV = 1  # [urad -> urad]

    DEVICES = _get_namedtuple(
        'Devices',
        (
            'TB_CH', 'TB_CV', 'TS_CH', 'TS_CV',
            'BO_CH', 'BO_CV', 'SI_CH', 'SI_CV', 'SI_FCH', 'SI_FCV'
        )
    )
    PROPTIES = _get_namedtuple(
        'Propties',
        (
            'Curr_Mon', 'Curr_Ref', 'Curr_SP', 'Curr_RB',
            'Kick_Mon', 'Kick_Ref', 'Kick_SP', 'Kick_RB',),
        (
            'Current-Mon', 'CurrentRef-Mon', 'Current-SP', 'Current-RB',
            'Kick-Mon', 'KickRef-Mon', 'Kick-SP', 'Kick-RB'))

    def __init__(self, devname='SI_CH', propty='Current-Mon', connector=None):
        """."""
        super().__init__(devname, propty=propty, connector=connector)

    # --- private methods ---
    def _get_pvnames(self):
        sec, dev = self._devname.split('_')
        devnames = _PSSearch.get_psnames({'sec': sec, 'dev': dev})
        pvnames = tuple(dev+':'+self._propty for dev in devnames)
        return devnames, pvnames


class TrimQuads(BaseDevice):
    """."""

    _CONV = 1  # [urad -> urad]

    DEVICES = _get_namedtuple(
        'Devices', ('TB_QN', 'TS_QN', 'SI_QN', 'SI_QS'))
    PROPTIES = _get_namedtuple(
        'Propties',
        (
            'Curr_Mon', 'Curr_Ref', 'Curr_SP', 'Curr_RB',
            'KL_Mon', 'KL_Ref', 'KL_SP', 'KL_RB',),
        (
            'Current-Mon', 'CurrentRef-Mon', 'Current-SP', 'Current-RB',
            'KL-Mon', 'KLRef-Mon', 'KL-SP', 'KL-RB'))

    def __init__(self, devname='SI_QS', propty='Current-Mon', connector=None):
        """."""
        super().__init__(devname, propty=propty, connector=connector)

    # --- private methods ---
    def _get_pvnames(self):
        sec, dev = self._devname.split('_')
        if dev == 'QN':
            devnames = _PSSearch.get_psnames({'sec': sec, 'dev': 'Q[DF1-9]'})
            devnames = [dev for f in devnames if 'Fam' not in dev]
        else:
            devnames = _PSSearch.get_psnames({'sec': sec, 'dev': dev})
        pvnames = tuple(dev+':'+self._propty for dev in devnames)
        return devnames, pvnames
