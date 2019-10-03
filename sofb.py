#!/usr/bin/env python-sirius

import time as _time
from epics import PV
from siriuspy.csdevice.orbitcorr import SOFBFactory


class SOFB:

    def __init__(self, acc):
        self.data = SOFBFactory.create(acc)
        orbtp = 'MTurnIdx' if acc == 'BO' else 'SPass'
        self._trajx = PV(acc+'-Glob:AP-SOFB:'+orbtp+'OrbX-Mon')
        self._trajy = PV(acc+'-Glob:AP-SOFB:'+orbtp+'OrbY-Mon')
        self._rst = PV(acc+'-Glob:AP-SOFB:SmoothReset-Cmd')
        self._npts_sp = PV(acc+'-Glob:AP-SOFB:SmoothNrPts-SP')
        self._npts_rb = PV(acc+'-Glob:AP-SOFB:BufferCount-Mon')
        self._sum = PV(acc+'-Glob:AP-SOFB:'+orbtp+'Sum-Mon')
        self._trigsample_sp = PV(acc+'-Glob:AP-SOFB:TrigNrSamplesPost-SP')
        self._trigsample_rb = PV(acc+'-Glob:AP-SOFB:TrigNrSamplesPost-RB')

    @property
    def connected(self):
        conn = self._trajx.connected
        conn &= self._trajy.connected
        conn &= self._sum.connected
        conn &= self._rst.connected
        conn &= self._npts_sp.connected
        conn &= self._npts_rb.connected
        return conn

    @property
    def trajx(self):
        return self._trajx.get()

    @property
    def trajy(self):
        return self._trajy.get()

    @property
    def sum(self):
        return self._sum.get()

    @property
    def nr_points(self):
        return self._npts_rb.value

    @nr_points.setter
    def nr_points(self, value):
        self._npts_sp.value = int(value)

    @property
    def trigsample(self):
        return self._trigsample_rb.value

    @trigsample.setter
    def trigsample(self, value):
        self._trigsample_sp.value = int(value)

    def wait(self, timeout=10):
        inter = 0.05
        n = int(timeout/inter)
        for _ in range(n):
            if self._npts_rb.value >= self._npts_sp.value:
                break
            _time.sleep(inter)
        else:
            print('WARN: Timed out waiting orbit.')

    def reset(self):
        self._rst.value = 1
