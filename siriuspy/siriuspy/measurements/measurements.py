
from functools import partial as _part
import numpy as _np
from epics import PV as _PV
import mathphys.constants as _consts
from siriuspy.thread import RepeaterThread as _Repeater
from siriuspy.search import PSSearch as _PSS
from siriuspy.factory import NormalizerFactory as _NormFact
from .calculations import CalcEnergy, ProcessImage
from .base import BaseClass as _BaseClass

C = _consts.light_speed
E0 = _consts.electron_rest_energy / _consts.elementary_charge * 1e-9  # in GeV


class MeasEnergy(_BaseClass):
    """."""

    def __init__(self):
        """."""
        self.energy_calculator = CalcEnergy()
        self.image_processor = ProcessImage()
        self.image_processor.readingorder = self.image_processor.CLIKE
        self._coefx = _PV(
            prof+':X:Gauss:Coef', callback=_part(self._update_coef, pln='x'))
        self._coefy = _PV(
            prof+':Y:Gauss:Coef', callback=_part(self._update_coef, pln='y'))
        self._image_source = _PV(prof + ':RAW:ArrayData')
        self._width_source = _PV(prof + ':ROI:MaxSizeX_RBV')
        self._current_source = _PV('LA-CN:H1DPPS-1:seti')
        self._interval = 0.5
        self._measuring = False
        self._thread = _Repeater(self._interval, self._meas_energy, niter=0)
        self._thread.start()

    def start(self):
        """."""
        self._measuring = True

    def stop(self):
        """."""
        self._measuring = False

    @property
    def rate(self):
        """."""
        return 1/self._interval

    @rate.setter
    def rate(self, val):
        if isinstance(val, (float, int)) and 0 < val < 4:
            self._interval = val
            self._thread.interval = val

    @property
    def measuring(self):
        """."""
        return self._measuring

    @measuring.setter
    def measuring(self, val):
        if val:
            self.start()
        else:
            self.stop()

    def _update_coef(self, _, val, pln='x', **kwargs):
        if val is None:
            return
        if pln.startswith('x'):
            self.image_processor.pxl2mmscalex = val
        elif pln.startswith('y'):
            self.image_processor.pxl2mmscaley = val

    def _meas_energy(self):
        if not self._measuring:
            return
        self.image_processor.imagewidth = self._width_source.get()
        self.image_processor.image = self._image_source.get()
        self.energy_calculator.set_data(
            self._current_source.get(),
            self.image_processor.beamcentermmx,
            self.image_processor.beamsizemmx)


class CalcEmmitance(_BaseClass):
    X = 0
    Y = 1
    PLACES = ('li', 'tb-qd2a', 'tb-qf2a')
    TRANSMAT = 0
    THINLENS = 1

    def __init__(self):
        self._place = 'LI'
        self._quadname = ''
        self._quadlen = 0.0
        self._distance = 0.0
        self._select_experimental_setup()
        self._beamsize = _np.array([], dtype=float)
        self._beamsize_fit = _np.array([], dtype=float)
        self._currents = _np.array([], dtype=float)
        self._quadstren = _np.array([], dtype=float)
        self._plane = self.X
        self._energy = 0.15
        self._emittance = 0.0
        self._beta = 0.0
        self._alpha = 0.0
        self._gamma = 0.0

    @property
    def place(self):
        return self._place

    @place.setter
    def place(self, val):
        if isinstance(val, str) and val.lower() in self.PLACES:
            self._place = val
            self._select_experimental_setup()
            self._perform_analysis()

    @property
    def plane(self):
        return self._plane

    @plane.setter
    def plane(self, val):
        if not isinstance(val, (int, float)):
            return
        self._plane = self.X if val == self.X else self.Y
        self._perform_analysis()

    @property
    def plane_str(self):
        return self._plane

    @plane_str.setter
    def plane_str(self, val):
        if not isinstance(val, str):
            return
        self.plane = self.X if val.lower == 'x' else self.Y

    @property
    def quadname(self):
        return self._quadname

    @property
    def quadlen(self):
        return self._quadlen

    @property
    def distance(self):
        return self._distance

    @property
    def beamsize(self):
        return self._beamsize.copy()

    @property
    def beamsize_fit(self):
        return self._beamsize_fit.copy()

    @property
    def currents(self):
        return self._currents.copy()

    @property
    def quadstren(self):
        return self._quadstren.copy()

    @property
    def beta(self):
        return self._beta

    @property
    def alpha(self):
        return self._alpha

    @property
    def gamma(self):
        return self._gamma

    @property
    def emittance(self):
        return self._emittance * 1e6  # in mm.mrad

    @property
    def norm_emittance(self):
        return self.emittance * self._energy / E0

    def set_data(self, beam_sizes, currents):
        if isinstance(beam_sizes, (int, float)):
            beam_sizes = [beam_sizes]
        if isinstance(currents, (int, float)):
            currents = [currents]
        beam_sizes = _np.array(beam_sizes, dtype=float)
        currents = _np.array(currents, dtype=float)
        if beam_sizes.size != currents.size:
            return False
        self._beamsize = beam_sizes
        self._currents = currents
        self._perform_analysis()

    def _select_experimental_setup(self):
        if self.place.lower().startswith('li'):
            self._quadname = 'LA-CN:H1FQPS-3'
            self._quadlen = 0.112
            self._distance = 2.8775
        if self.place.lower().startswith('tb-qd2a'):
            self._quadname = 'TB-02:PS-QD2A'
            self._quadlen = 0.1
            self._distance = 6.904
        if self.place.lower().startswith('tb-qf2a'):
            self._quadname = 'TB-02:PS-QF2A'
            self._quadlen = 0.1
            self._distance = 6.534
        self._conv2kl = _NormFact.create(self._quadname)
