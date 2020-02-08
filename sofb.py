#!/usr/bin/env python-sirius
"""."""

import time as _time
from epics import PV
from siriuspy.csdevice.orbitcorr import SOFBFactory


class SOFB:
    """."""

    def __init__(self, acc):
        """."""
        self.data = SOFBFactory.create(acc)
        orbtp = 'MTurn' if self.data.isring else 'SPass'
        pref = acc.upper() + '-Glob:AP-SOFB:'
        self._trajx = PV(pref+orbtp+'OrbX-Mon')
        self._trajy = PV(pref+orbtp+'OrbY-Mon')
        self._orbx = PV(pref+'SlowOrbX-Mon', auto_monitor=False)
        self._orby = PV(pref+'SlowOrbY-Mon', auto_monitor=False)
        self._kickch = PV(pref+'KickCH-Mon', auto_monitor=False)
        self._kickcv = PV(pref+'KickCV-Mon', auto_monitor=False)
        self._deltakickch = PV(pref+'DeltaKickCH-Mon')
        self._deltakickcv = PV(pref+'DeltaKickCV-Mon')
        self._refx_sp = PV(pref+'RefOrbX-SP')
        self._refy_sp = PV(pref+'RefOrbY-SP')
        self._refx_rb = PV(pref+'RefOrbX-RB')
        self._refy_rb = PV(pref+'RefOrbY-RB')
        self._bpmxenbl_sp = PV(pref+'BPMXEnblList-SP')
        self._bpmyenbl_sp = PV(pref+'BPMYEnblList-SP')
        self._bpmxenbl_rb = PV(pref+'BPMXEnblList-RB')
        self._bpmyenbl_rb = PV(pref+'BPMYEnblList-RB')
        self._chenbl_sp = PV(pref+'CHEnblList-SP')
        self._cvenbl_sp = PV(pref+'CVEnblList-SP')
        self._chenbl_rb = PV(pref+'CHEnblList-RB')
        self._cvenbl_rb = PV(pref+'CVEnblList-RB')
        self._calccorr = PV(pref+'CalcDelta-Cmd')
        self._applycorr = PV(pref+'ApplyDelta-Cmd')
        if self.data.isring:
            self._trajx_idx = PV(pref+orbtp+'Idx'+'OrbX-Mon')
            self._trajy_idx = PV(pref+orbtp+'Idx'+'OrbY-Mon')
        self._rst = PV(pref+'SmoothReset-Cmd')
        self._npts_sp = PV(pref+'SmoothNrPts-SP')
        self._npts_rb = PV(pref+'BufferCount-Mon')
        self._sum = PV(pref+orbtp+'Sum-Mon')
        self._trigsample_sp = PV(pref+'TrigNrSamplesPost-SP')
        self._trigsample_rb = PV(pref+'TrigNrSamplesPost-RB')

    @property
    def connected(self):
        """."""
        conn = self._trajx.connected
        conn &= self._trajy.connected
        conn &= self._orbx.connected
        conn &= self._orby.connected
        conn &= self._kickch.connected
        conn &= self._kickcv.connected
        conn &= self._deltakickch.connected
        conn &= self._deltakickcv.connected
        conn &= self._refx_sp.connected
        conn &= self._refy_sp.connected
        conn &= self._refx_rb.connected
        conn &= self._refy_rb.connected
        conn &= self._bpmxenbl_sp.connected
        conn &= self._bpmyenbl_sp.connected
        conn &= self._bpmxenbl_rb.connected
        conn &= self._bpmyenbl_rb.connected
        conn &= self._chenbl_sp.connected
        conn &= self._cvenbl_sp.connected
        conn &= self._chenbl_rb.connected
        conn &= self._cvenbl_rb.connected
        conn &= self._sum.connected
        conn &= self._rst.connected
        conn &= self._calccorr.connected
        conn &= self._applycorr.connected
        conn &= self._npts_sp.connected
        conn &= self._npts_rb.connected
        return conn

    @property
    def trajx(self):
        """."""
        return self._trajx.get()

    @property
    def trajy(self):
        """."""
        return self._trajy.get()

    @property
    def orbx(self):
        """."""
        return self._orbx.get()

    @property
    def orby(self):
        """."""
        return self._orby.get()

    @property
    def trajx_idx(self):
        """."""
        return self._trajx_idx.get() if self.data.isring \
            else self.trajx

    @property
    def trajy_idx(self):
        """."""
        return self._trajy_idx.get() if self.data.isring \
            else self.trajy

    @property
    def sum(self):
        """."""
        return self._sum.get()

    @property
    def kickch(self):
        """."""
        return self._kickch.get()

    @property
    def kickcv(self):
        """."""
        return self._kickcv.get()

    @property
    def deltakickch(self):
        """."""
        return self._deltakickch.get()

    @property
    def deltakickcv(self):
        """."""
        return self._deltakickcv.get()

    @property
    def refx(self):
        """."""
        return self._refx_rb.value

    @refx.setter
    def refx(self, value):
        self._refx_sp.value = value

    @property
    def refy(self):
        """."""
        return self._refy_rb.value

    @refy.setter
    def refy(self, value):
        self._refy_sp.value = value

    @property
    def bpmxenbl(self):
        """."""
        return self._bpmxenbl_rb.value

    @bpmxenbl.setter
    def bpmxenbl(self, value):
        self._bpmxenbl_sp.value = value

    @property
    def bpmyenbl(self):
        """."""
        return self._bpmyenbl_rb.value

    @bpmyenbl.setter
    def bpmyenbl(self, value):
        self._bpmyenbl_sp.value = value

    @property
    def chenbl(self):
        """."""
        return self._chenbl_rb.value

    @chenbl.setter
    def chenbl(self, value):
        self._chenbl_sp.value = value

    @property
    def cvenbl(self):
        """."""
        return self._cvenbl_rb.value

    @cvenbl.setter
    def cvenbl(self, value):
        self._cvenbl_sp.value = value

    @property
    def nr_points(self):
        """."""
        return self._npts_rb.value

    @nr_points.setter
    def nr_points(self, value):
        self._npts_sp.value = int(value)

    @property
    def trigsample(self):
        """."""
        return self._trigsample_rb.value

    @trigsample.setter
    def trigsample(self, value):
        self._trigsample_sp.value = int(value)

    def wait(self, timeout=10):
        """."""
        inter = 0.05
        n = int(timeout/inter)
        _time.sleep(4*inter)
        for _ in range(n):
            if self._npts_rb.value >= self._npts_sp.value:
                break
            _time.sleep(inter)
        else:
            print('WARN: Timed out waiting orbit.')

    def reset(self):
        """."""
        self._rst.value = 1

    def calccorr(self):
        self._calccorr.value = 1

    def applycorr(self):
        """."""
        self._applycorr.value = self.data.ApplyDelta.CH
        _time.sleep(0.3)
        self._applycorr.value = self.data.ApplyDelta.CV

