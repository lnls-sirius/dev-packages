#!/usr/bin/env python-sirius

from epics import PV
from siriuspy.namesys import SiriusPVName


class Screen:

    def __init__(self, name):
        self._name = SiriusPVName(name)
        self._image = PV(self._name.substitute(propty='ImgData-Mon'))
        self._centerx = PV(self._name.substitute(propty='CenterXDimFei-Mon'))
        self._centery = PV(self._name.substitute(propty='CenterYDimFei-Mon'))
        self._sigmax = PV(self._name.substitute(propty='SigmaXDimFei-Mon'))
        self._sigmay = PV(self._name.substitute(propty='SigmaYDimFei-Mon'))

    @property
    def name(self):
        return self._name

    @property
    def connected(self):
        conn = self._image.connected
        conn &= self._centerx.connected
        conn &= self._centery.connected
        conn &= self._sigmax.connected
        conn &= self._sigmay.connected
        return conn

    @property
    def image(self):
        return self._image.get()

    @property
    def centerx(self):
        return self._centerx.value

    @property
    def centery(self):
        return self._centery.value

    @property
    def sigmax(self):
        return self._sigmax.value

    @property
    def sigmay(self):
        return self._sigmay.value
