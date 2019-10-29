#!/usr/bin/env python-sirius

import time as _time
from epics import PV
from siriuspy.namesys import SiriusPVName


class BPM:

    def __init__(self, name):
        self._name = SiriusPVName(name)
        self._spanta = PV(self._name.substitute(propty='SP_AArrayData'))
        self._spantb = PV(self._name.substitute(propty='SP_BArrayData'))
        self._spantc = PV(self._name.substitute(propty='SP_CArrayData'))
        self._spantd = PV(self._name.substitute(propty='SP_DArrayData'))

    @property
    def connected(self):
        conn = self._spanta.connected
        conn &= self._spantb.connected
        conn &= self._spantc.connected
        conn &= self._spantd.connected
        return conn

    @property
    def sp_anta(self):
        return self._spanta.get()

    @property
    def sp_antb(self):
        return self._spantb.get()

    @property
    def sp_antc(self):
        return self._spantc.get()

    @property
    def sp_antd(self):
        return self._spantd.get()
