#!/usr/bin/env python-sirius

import time as _time
from epics import PV


class DCCT:

    def __init__(self):
        self._current = PV('BO-35D:DI-DCCT:RawReadings-Mon')
        self._meas_per_sp = PV('BO-35D:DI-DCCT:FastMeasPeriod-SP')
        self._meas_per_rb = PV('BO-35D:DI-DCCT:FastMeasPeriod-RB')
        self._nr_samples_sp = PV('BO-35D:DI-DCCT:FastSampleCnt-SP')
        self._nr_samples_rb = PV('BO-35D:DI-DCCT:FastSampleCnt-RB')
        self._acq_ctrl_sp = PV('BO-35D:DI-DCCT:MeasTrg-Sel')
        self._acq_ctrl_rb = PV('BO-35D:DI-DCCT:MeasTrg-Sts')
        self._on_state = 1
        self._off_state = 0

    @property
    def connected(self):
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
        return self._nr_samples_rb.value

    @nrsamples.setter
    def nrsamples(self, value):
        self._nr_samples_sp.value = value

    @property
    def period(self):
        return self._meas_per_rb.value

    @period.setter
    def period(self, value):
        self._meas_per_sp.value = value

    @property
    def acq_ctrl(self):
        return self._acq_ctrl_rb.value

    @acq_ctrl.setter
    def acq_ctrl(self, value):
        self._acq_ctrl_sp.value = self._on_state if value else self._off_state

    @property
    def current(self):
        return self._current.get()

    def wait(self, timeout=10):
        nrp = int(timeout/0.1)
        for _ in range(nrp):
            _time.sleep(0.1)
            if self._isok():
                break
        else:
            print('timed out waiting DCCT.')

    def _isok(self):
        if self._acq_ctrl_sp.value:
            return self.acq_ctrl == self._on_state
        else:
            return self.acq_ctrl != self._on_state

    def turn_on(self, timeout=10):
        self.acq_ctrl = self._on_state
        self.wait(timeout)

    def turn_off(self, timeout=10):
        self.acq_ctrl = self._off_state
        self.wait(timeout)
