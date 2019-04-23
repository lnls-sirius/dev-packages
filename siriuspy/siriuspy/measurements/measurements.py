
from functools import partial as _part
from copy import deepcopy as _dcopy
import numpy as _np
from scipy.optimize import curve_fit
from epcallbackics import PV as _PV
import mathphys.constants as _consts
from siriuspy.thread import RepeaterThread as _Repeater
from siriuspy.search import PSSearch as _PSS
from siriuspy.factory import NormalizerFactory as _NormFact
from .calculations import CalcEnergy, ProcessImage

C = _consts.light_speed
E0 = _consts.electron_rest_energy / _consts.elementary_charge * 1e-9  # in GeV


class MeasEnergy:
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


class CalcEmmitance:
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

    def _perform_analysis(self):
        if not self._beamsize.size:
            return
        self._update_quad_strength()
        self._trans_matrix_analysis()
        self._thin_lens_approx()

    def _update_quad_strength(self):
        KL = self._conv2kl.conv_current_2_strength(
            self._currents, strengths_dipole=self._energy)
        self._quadstren = KL/self._quadlen
        if self._plane == self.Y:
            self._quadstren *= -1

    def _thin_lens_approx(self):
        fit = _np.polyfit(self._quadstren, self._beamsize**2, 2)
        self._beamsize_fit = _np.sqrt(_np.polyval(fit, self._quadstren))
        # d = self.distance + self.quad_length/2
        # l = self.quad_length
        # s_11 = fit[0]/(d*l)**2
        # s_12 = (-fit[1]-2*d*l*s_11)/(2*l*d*d)
        # s_22 = (fit[2]-s_11-2*d*s_12)/d**2
        # self._update_twiss(s_11, s_12, s_22)

    def _trans_matrix_analysis(self):
        R = self._get_trans_mat()
        pseudo_inv = (_np.linalg.inv(_np.transpose(R) @ R) @ _np.transpose(R))
        [s_11, s_12, s_22] = pseudo_inv @ (self._beamsize**2)
        # s_11, s_12, s_22 = np.linalg.lstsq(R, self._beamsize**2)[0]
        self._update_twiss(s_11, s_12, s_22)

    def _get_trans_mat(self):
        R = _np.zeros((self._quadstren.size, 2, 2))
        Rd = self.gettransmat('drift', L=self._distance)
        for i, k1 in enumerate(self._quadstren):
            Rq = self.gettransmat('quad', L=self._quadlen, K1=k1)
            R[i] = _np.dot(Rd, Rq)
        R11 = R[:, 0, 0].reshape(-1)
        R12 = R[:, 0, 1].reshape(-1)
        R = _np.column_stack((R11*R11, 2*R11*R12, R12*R12))
        return R

    def _update_twiss(self, s_11, s_12, s_22):
        self._emittance = _np.sqrt(abs(s_11*s_22 - s_12*s_12))
        self._beta = s_11 / self._emittance
        self._alpha = -s_12 / self._emittance
        self._gamma = s_22 / self._emittance

    @staticmethod
    def gettransmat(elem, L, K1=None, B=None):
        M = _np.eye(2)
        if elem.lower().startswith('qu') and K1 is not None and K1 == 0:
            elem = 'drift'
        if elem.lower().startswith('dr'):
            M = _np.array([[1, L], [0, 1], ])
        elif elem.lower().startswith('qu') and K1 is not None:
            kq = _np.sqrt(abs(K1))
            if K1 > 0:
                c = _np.cos(kq*L)
                s = _np.sin(kq*L)
                m11, m12, m21 = c, 1/kq*s, -kq*s
            else:
                ch = _np.cosh(kq*L)
                sh = _np.sinh(kq*L)
                m11, m12, m21 = ch, 1/kq*sh, kq*sh
            M = _np.array([[m11, m12], [m21, m11], ])
        return M
