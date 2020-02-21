#!/usr/bin/env python-sirius
"""."""

import time as _time
from collections import namedtuple
from epics import PV


class DCCT:
    """."""

    STATUS = namedtuple('Status', 'Off On')(0, 1)
    NAME_BO = 'bo'
    NAME_SI_1 = 'si-1'
    NAME_SI_2 = 'si-2'

    def __init__(self, name):
        """."""
        if not set(self.NAME_BO) - set(name.lower()):
            name = 'BO-35D:DI-DCCT:'
        elif not set(self.NAME_SI_1) - set(name.lower()):
            name = 'SI-13C4:DI-DCCT:'
        elif not set(self.NAME_SI_2) - set(name.lower()):
            name = 'SI-14C4:DI-DCCT:'
        else:
            raise Exception('Set DCCT name: BO, SI-1 or SI-2')
        self._current = PV(name+'RawReadings-Mon')
        self._meas_per_sp = PV(name+'FastMeasPeriod-SP')
        self._meas_per_rb = PV(name+'FastMeasPeriod-RB')
        self._nr_samples_sp = PV(name+'FastSampleCnt-SP')
        self._nr_samples_rb = PV(name+'FastSampleCnt-RB')
        self._acq_ctrl_sp = PV(name+'MeasTrg-Sel')
        self._acq_ctrl_rb = PV(name+'MeasTrg-Sts')


    @property
    def connected(self):
        """."""
        conn = self._current.connected
        conn &= self._meas_per_sp.connected
        conn &= self._meas_per_rb.connected
        conn &= self._nr_samples_sp.connected
        conn &= self._nr_samples_rb.connected
        conn &= self._acq_ctrl_sp.connected
        conn &= self._acq_ctrl_rb.connected
        return conn

    @property
    def nrsamples(self):
        """."""
        return self._nr_samples_rb.value

    @nrsamples.setter
    def nrsamples(self, value):
        self._nr_samples_sp.value = value

    @property
    def period(self):
        """."""
        return self._meas_per_rb.value

    @period.setter
    def period(self, value):
        self._meas_per_sp.value = value

    @property
    def acq_ctrl(self):
        """."""
        return self._acq_ctrl_rb.value

    @acq_ctrl.setter
    def acq_ctrl(self, value):
        self._acq_ctrl_sp.value = self.STATUS.On if value else self.STATUS.Off

    @property
    def current(self):
        """."""
        return self._current.get()

    def wait(self, timeout=10):
        """."""
        nrp = int(timeout/0.1)
        for _ in range(nrp):
            _time.sleep(0.1)
            if self._isok():
                break
        else:
            print('timed out waiting DCCT.')

    def _isok(self):
        if self._acq_ctrl_sp.value:
            return self.acq_ctrl == self.STATUS.On
        else:
            return self.acq_ctrl != self.STATUS.On

    def turn_on(self, timeout=10):
        """."""
        self.acq_ctrl = self.STATUS.On
        self.wait(timeout)

    def turn_off(self, timeout=10):
        """."""
        self.acq_ctrl = self.STATUS.Off
        self.wait(timeout)
