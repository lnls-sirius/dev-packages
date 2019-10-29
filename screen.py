#!/usr/bin/env python-sirius

from epics import PV
from siriuspy.namesys import SiriusPVName


class Screen:

    def __init__(self, name):
        self._name = SiriusPVName(name)
        self._image = PV(self._name.substitute(propty='ImgData-Mon'))

    @property
    def name(self):
        return self._name

    @property
    def connected(self):
        conn = self._image.connected
        return conn

    @property
    def image(self):
        return self._image.get()
