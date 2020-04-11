"""."""

from functools import partial as _part
from threading import Event as _Event
import numpy as _np
from epics import PV as _PV

import mathphys.constants as _consts

from ...magnet.factory import NormalizerFactory as _NormFact

from ..util import BaseClass as _BaseClass, ProcessImage as _ProcessImage

C = _consts.light_speed
E0 = _consts.electron_rest_energy / _consts.elementary_charge * 1e-6  # in MeV


class CalcEmmitance(_BaseClass):
    """."""

    X = 0
    Y = 1
    PLACES = ('li', 'tb-qd2a', 'tb-qf2a')

    def __init__(self):
        """."""
        super().__init__()
        self._place = 'LI'
        self._quadname = ''
        self._quadlen = 0.0
        self._distance = 0.0
        self._select_experimental_setup()
        self._beamsize = _np.array([], dtype=float)
        self._beamsize_fit = _np.array([], dtype=float)
        self._currents = _np.array([], dtype=float)
        self._quadstren = _np.array([], dtype=float)
        self._plane = self.Plane.X
        self._energy = 0.15
        self._emittance = 0.0
        self._beta = 0.0
        self._alpha = 0.0
        self._gamma = 0.0

    def get_map2write(self):
        """."""
        return {
            'Place-Sel': _part(self.write, 'place'),
            'Plane-Sel': _part(self.write, 'plane'),
            }

    def get_map2read(self):
        """."""
        return {
            'Place-Sts': _part(self.read, 'place'),
            'Plane-Sts': _part(self.read, 'plane'),
            'QuadName-Mon': _part(self.read, 'quadname'),
            'QuadLen-Mon': _part(self.read, 'quadlen'),
            'Distance-Mon': _part(self.read, 'distance'),
            'BeamSizes-Mon': _part(self.read, 'beamsize'),
            'BeamSizesFit-Mon': _part(self.read, 'beamsize_fit'),
            'QuadCurrents-Mon': _part(self.read, 'currents'),
            'QuadStrens-Mon': _part(self.read, 'quadstren'),
            'Beta-Mon': _part(self.read, 'beta'),
            'Alpha-Mon': _part(self.read, 'alpha'),
            'Gamma-Mon': _part(self.read, 'gamma'),
            'Emittance-Mon': _part(self.read, 'emittance'),
            'NormEmittance-Mon': _part(self.read, 'norm_emittance'),
            }

    @property
    def place(self):
        """."""
        return self._place

    @place.setter
    def place(self, val):
        """."""
        if isinstance(val, str) and val.lower() in self.PLACES:
            self._place = val
            self._select_experimental_setup()
            self._perform_analysis()

    @property
    def plane(self):
        """."""
        return self._plane

    @plane.setter
    def plane(self, val):
        """."""
        if int(val) in self.Plane:
            self._plane = int(val)
        self._perform_analysis()

    @property
    def plane_str(self):
        """."""
        return self.Plane._fields[self._plane]

    @plane_str.setter
    def plane_str(self, val):
        """."""
        if val in self.Plane._fields:
            self.plane = self.Plane._fields.index(val)

    @property
    def quadname(self):
        """."""
        return self._quadname

    @property
    def quadlen(self):
        """."""
        return self._quadlen

    @property
    def distance(self):
        """."""
        return self._distance

    @property
    def beamsize(self):
        """."""
        return self._beamsize.copy()

    @property
    def beamsize_fit(self):
        """."""
        return self._beamsize_fit.copy()

    @property
    def currents(self):
        """."""
        return self._currents.copy()

    @property
    def quadstren(self):
        """."""
        return self._quadstren.copy()

    @property
    def beta(self):
        """."""
        return self._beta

    @property
    def alpha(self):
        """."""
        return self._alpha

    @property
    def gamma(self):
        """."""
        return self._gamma

    @property
    def emittance(self):
        """."""
        return self._emittance * 1e6  # in mm.mrad

    @property
    def norm_emittance(self):
        """."""
        return self.emittance * self._energy / E0

    def set_data(self, beam_sizes, currents):
        """."""
        if None in {currents, beam_sizes}:
            return False
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
        return True

    def _select_experimental_setup(self):
        """."""
        if self.place.lower().startswith('li'):
            self._quadname = 'LI-01:PS-QF3'
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
        """."""
        if not self._beamsize.size:
            return
        self._update_quad_strength()
        self._trans_matrix_analysis()
        self._thin_lens_approx()

    def _update_quad_strength(self):
        """."""
        KL = self._conv2kl.conv_current_2_strength(
            self._currents, strengths_dipole=self._energy)
        self._quadstren = KL/self._quadlen
        if self._plane == self.Plane.Y:
            self._quadstren *= -1

    def _thin_lens_approx(self):
        """."""
        fit = _np.polyfit(self._quadstren, self._beamsize**2, 2)
        self._beamsize_fit = _np.sqrt(_np.polyval(fit, self._quadstren))
        # d = self.distance + self.quad_length/2
        # l = self.quad_length
        # s_11 = fit[0]/(d*l)**2
        # s_12 = (-fit[1]-2*d*l*s_11)/(2*l*d*d)
        # s_22 = (fit[2]-s_11-2*d*s_12)/d**2
        # self._update_twiss(s_11, s_12, s_22)

    def _trans_matrix_analysis(self):
        """."""
        R = self._get_trans_mat()
        pseudo_inv = (_np.linalg.inv(_np.transpose(R) @ R) @ _np.transpose(R))
        [s_11, s_12, s_22] = pseudo_inv @ (self._beamsize**2)
        # s_11, s_12, s_22 = np.linalg.lstsq(R, self._beamsize**2)[0]
        self._update_twiss(s_11, s_12, s_22)

    def _get_trans_mat(self):
        """."""
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
        """."""
        self._emittance = _np.sqrt(abs(s_11*s_22 - s_12*s_12))
        self._beta = s_11 / self._emittance
        self._alpha = -s_12 / self._emittance
        self._gamma = s_22 / self._emittance

    @staticmethod
    def gettransmat(elem, L, K1=None, B=None):
        """."""
        matrix = _np.eye(2)
        if elem.lower().startswith('qu') and K1 is not None and K1 == 0:
            elem = 'drift'
        if elem.lower().startswith('dr'):
            matrix = _np.array([[1, L], [0, 1], ])
        elif elem.lower().startswith('qu') and K1 is not None:
            vkq = _np.sqrt(abs(K1))
            if K1 > 0:
                cos = _np.cos(vkq*L)
                sin = _np.sin(vkq*L)
                m11, m12, m21 = cos, 1/vkq*sin, -vkq*sin
            else:
                hcos = _np.cosh(vkq*L)
                hsin = _np.sinh(vkq*L)
                m11, m12, m21 = hcos, 1/vkq*hsin, vkq*hsin
            matrix = _np.array([[m11, m12], [m21, m11], ])
        return matrix


class MeasEmmitance(_BaseClass):
    """."""

    X = 0
    Y = 1
    PLACES = ('li', 'tb-qd2a', 'tb-qf2a')

    def __init__(self):
        """."""
        super().__init__()
        self._measuring = _Event()
        self.emittance_calculator = CalcEmmitance()
        self.image_processor = _ProcessImage()
        self.image_processor.readingorder = \
            self.image_processor.ReadingOrder.CLike
        self._place = 'li'
        self._select_experimental_setup()

    def get_map2write(self):
        """."""
        database = dict()
        dic_ = self.image_processor.get_map2write()
        dic_.update(self.emittance_calculator.get_map2write())
        dic_.update({'MeasureCtrl-Sel': _part(self.write, 'measuring')})
        return {k: v for k, v in dic_.items() if k in database}

    def get_map2read(self):
        """."""
        database = dict()
        dic_ = self.image_processor.get_map2read()
        dic_.update(self.emittance_calculator.get_map2read())
        dic_.update({'MeasureCtrl-Sts': _part(self.read, 'measuring')})
        return {k: v for k, v in dic_.items() if k in database}

    @property
    def place(self):
        """."""
        return self._place

    @place.setter
    def place(self, val):
        """."""
        if val in self.PLACES:
            self._place = val
            self._select_experimental_setup()

    def _select_experimental_setup(self):
        """."""
        self.emittance_calculator.place = self._place
        if self._place.lower().startswith('li'):
            prof = 'LA-BI:PRF5'
            self._image_source = _PV(prof+':RAW:ArrayData')
            self._width_source = _PV(
                prof+':ROI:MaxSizeX_RBV', callback=self._update_width)
            self._coefx = _PV(
                prof+':X:Gauss:Coef',
                callback=self._update_coefx)
            self._coefy = _PV(
                prof+':Y:Gauss:Coef',
                callback=self._update_coefy)
            self.quad_I_sp = _PV('LI-01:PS-QF3:Current-SP')
            self.quad_I_rb = _PV('LI-01:PS-QF3:Current-Mon')
        elif self._place.lower().startswith('tb'):
            self._image_source = _PV('TB-02:DI-Scrn-2:ImgData-Mon')
            self._width_source = _PV(
                'TB-02:DI-Scrn-2:ImgMaxWidth-Cte', callback=self._update_width)
            self._coefx = _PV(
                'TB-02:DI-ScrnCam-2:ImgScaleFactorX-RB',
                callback=self._update_coefx)
            self._coefy = _PV(
                'TB-02:DI-ScrnCam-2:ImgScaleFactorY-RB',
                callback=self._update_coefy)
            quad = self.emittance_calculator.quadname
            self.quad_I_sp = _PV(quad + ':Current-SP')
            self.quad_I_rb = _PV(quad + ':Current-RB')

    def _update_coefx(self, pvname, value, **kwargs):
        """."""
        if value is None:
            return
        self.image_processor.pxl2mmscalex = value

    def _update_coefy(self, pvname, value, **kwargs):
        """."""
        if value is None:
            return
        self.image_processor.pxl2mmscaley = value

    def _update_width(self, pvname, value, **kwargs):
        """."""
        if isinstance(value, (float, int)):
            self.image_processor.imagewidth = int(value)

    def _acquire_data(self):
        """."""
        samples = self.spbox_samples.value()
        nsteps = self.spbox_steps.value()
        I_ini = self.spbox_I_ini.value()
        I_end = self.spbox_I_end.value()

        pl = 'y' if self.cbbox_plane.currentIndex() else 'x'
        curr_list = _np.linspace(I_ini, I_end, nsteps)
        sigma = []
        I_meas = []
        for i, I in enumerate(curr_list):
            print('setting Quadrupole to ', I)
            self.quad_I_sp.put(I, wait=True)
            self._measuring.wait(5 if i else 15)
            j = 0
            I_tmp = []
            sig_tmp = []
            while j < samples:
                if self._measuring.is_set():
                    print('Stopped')
                    return
                print('measuring sample', j)
                I_now = self.quad_I_rb.value
                cen_x, sigma_x, cen_y, sigma_y = self.plt_image.get_params()
                mu, sig = (cen_x, sigma_x) if pl == 'x' else (cen_y, sigma_y)
                max_size = self.spbox_threshold.value()*1e-3
                if sig > max_size:
                    self._measuring.wait(1)
                    continue
                I_tmp.append(I_now)
                sig_tmp.append(abs(sig))
                self._measuring.wait(0.5)
                j += 1
            ind = np.argsort(sig_tmp)
            I_tmp = np.array(I_tmp)[ind]
            sig_tmp = np.array(sig_tmp)[ind]
            I_meas.extend(I_tmp[6:-6])
            sigma.extend(sig_tmp[6:-6])
        self._measuring.set()
        print('Finished!')
        self.I_meas = I_meas
        self.sigma = sigma
        self.plane_meas = pl
