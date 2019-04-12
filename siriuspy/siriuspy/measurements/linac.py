
import numpy as _np
from scipy.optimize import curve_fit
from siriuspy.search import PSSearch as _PSS
import mathphys.constants as _consts

C = _consts.light_speed
E0 = _consts.electron_rest_energy / _consts.elementary_charge * 1e-9  # in GeV


class ProcessImage:
    X = 1
    Y = 0
    AMP = 0
    CEN = 1
    SIG = 2
    OFF = 3
    LOW = 0
    HIGH = 1
    MOMENTS = 0
    GAUSS = 1

    def __init__(self):
        self._roi_autocenter = True
        self._roi_cen = [0, 0]
        self._roi_size = [0, 0]
        self._roi_start = [0, 0]
        self._roi_end = [0, 0]
        self._roi_axis = [_np.array([], dtype=int), _np.array([], dtype=int)]
        self._roi_proj = [_np.array([], dtype=int), _np.array([], dtype=int)]
        self._roi_gauss = [_np.array([], dtype=int), _np.array([], dtype=int)]
        self._background = _np.zeros((2, 2), dtype=int)
        self._background_use = False
        self._crop = [0, 255]
        self._crop_use = False
        self._method = self.GAUSS
        self._image_raw = _np.zeros((2, 2), dtype=int)
        self._image_proc = _np.zeros((2, 2), dtype=int)
        self._conv_autocenter = True
        self._conv_cen = [0, 0]
        self._conv_scale = [1, 1]
        self._beam_params = [[0, 1, 1, 0], [0, 1, 1, 0]]

    @property
    def image(self):
        return self._image_proc.copy()

    @image.setter
    def image(self, val):
        if not isinstance(val, _np.ndarray) or len(val.shape) != 2:
            return
        self._image_raw = val.copy()
        self._process_image()

    @property
    def imagecroplow(self):
        return self._crop[self.LOW]

    @imagecroplow.setter
    def imagecroplow(self, val):
        val = int(val)
        if 0 <= val < self._crop[self.HIGH]:
            self._crop[self.LOW] = val

    @property
    def imagecrophigh(self):
        return self._crop[self.HIGH]

    @imagecrophigh.setter
    def imagecrophigh(self, val):
        val = int(val)
        if self._crop[self.LOW] < val:
            self._crop[self.HIGH] = val

    @property
    def useimagecrop(self):
        return self._crop_use

    @useimagecrop.setter
    def useimagecrop(self, val):
        self._crop_use = bool(val)

    @property
    def imagesizex(self):
        return self._image_raw.shape[self.X]

    @property
    def imagesizey(self):
        return self._image_raw.shape[self.Y]

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, val):
        self._method = self.MOMENTS if int(val) == self.MOMENTS else self.GAUSS

    @property
    def roiautocenter(self):
        return self._roi_autocenter

    @roiautocenter.setter
    def roiautocenter(self, val):
        self._roi_autocenter = bool(val)

    @property
    def roicenterx(self):
        return self._roi_cen[self.X]

    @roicenterx.setter
    def roicenterx(self, val):
        if self._roi_autocenter:
            return
        val = int(val)
        if 0 <= val < self._image_raw.shape[self.X]:
            self._roi_cen[self.X] = val

    @property
    def roicentery(self):
        return self._roi_cen[self.Y]

    @roicentery.setter
    def roicentery(self, val):
        if self._roi_autocenter:
            return
        val = int(val)
        if 0 <= val < self._image_raw.shape[self.Y]:
            self._roi_cen[self.Y] = val

    @property
    def roisizex(self):
        return self._roi_size[self.X]

    @roisizex.setter
    def roisizex(self, val):
        val = int(val)
        if 1 <= val < self._image_raw.shape[self.X]:
            self._roi_size[self.X] = val

    @property
    def roisizey(self):
        return self._roi_size[self.Y]

    @roisizey.setter
    def roisizey(self, val):
        val = int(val)
        if 1 <= val < self._image_raw.shape[self.Y]:
            self._roi_size[self.Y] = val

    @property
    def roistartx(self):
        return self._roi_start[self.X]

    @property
    def roistarty(self):
        return self._roi_start[self.Y]

    @property
    def roiendx(self):
        return self._roi_end[self.X]

    @property
    def roiendy(self):
        return self._roi_end[self.Y]

    @property
    def roiprojx(self):
        return self._roi_proj[self.X].copy()

    @property
    def roiprojy(self):
        return self._roi_proj[self.Y].copy()

    @property
    def roiaxisx(self):
        return self._roi_axis[self.X].copy()

    @property
    def roiaxisy(self):
        return self._roi_axis[self.Y].copy()

    @property
    def roigaussx(self):
        return self._roi_gauss[self.X].copy()

    @property
    def roigaussy(self):
        return self._roi_gauss[self.Y].copy()

    @property
    def background(self):
        return self._background.copy()

    @background.setter
    def background(self, val):
        if not isinstance(val, _np.ndarray) or len(val.shape) != 2:
            return
        self._background = val.copy()

    @property
    def usebackground(self):
        return self._background_use

    @usebackground.setter
    def usebackground(self, val):
        self._background_use = bool(val)

    @property
    def beamcenterx(self):
        return self._beam_params[self.X][self.CEN]

    @property
    def beamcentery(self):
        return self._beam_params[self.Y][self.CEN]

    @property
    def beamsizex(self):
        return self._beam_params[self.X][self.SIG]

    @property
    def beamsizey(self):
        return self._beam_params[self.Y][self.SIG]

    @property
    def beamamplx(self):
        return self._beam_params[self.X][self.AMP]

    @property
    def beamamply(self):
        return self._beam_params[self.Y][self.AMP]

    @property
    def beamoffsetx(self):
        return self._beam_params[self.X][self.OFF]

    @property
    def beamoffsety(self):
        return self._beam_params[self.Y][self.OFF]

    @property
    def pxl2mmscalex(self):
        return self._conv_scale[self.X]

    @pxl2mmscalex.setter
    def pxl2mmscalex(self, val):
        if val != 0:
            self._conv_scale[self.X] = val

    @property
    def pxl2mmscaley(self):
        return self._conv_scale[self.Y]

    @pxl2mmscaley.setter
    def pxl2mmscaley(self, val):
        if val != 0:
            self._conv_scale[self.Y] = val

    @property
    def pxl2mmoffsetauto(self):
        return self._conv_autocenter

    @pxl2mmoffsetauto.setter
    def pxl2mmoffsetauto(self, val):
        self._conv_autocenter = bool(val)

    @property
    def pxl2mmoffsetx(self):
        return self._conv_cen[self.X]

    @pxl2mmoffsetx.setter
    def pxl2mmoffsetx(self, val):
        if self._conv_autocenter:
            return
        val = int(val)
        if 0 <= val < self._image_raw.shape[self.Y]:
            self._conv_cen[self.X] = val

    @property
    def pxl2mmoffsety(self):
        return self._conv_cen[self.Y]

    @pxl2mmoffsety.setter
    def pxl2mmoffsety(self, val):
        if self._conv_autocenter:
            return
        val = int(val)
        if 0 <= val < self._image_raw.shape[self.Y]:
            self._conv_cen[self.Y] = val

    @property
    def beamcentermmx(self):
        val = self.beamcenterx - self._conv_cen[self.X]
        val *= self._conv_scale[self.X]
        return val

    @property
    def beamcentermmy(self):
        val = self.beamcentery - self._conv_cen[self.Y]
        val *= self._conv_scale[self.Y]
        return val

    @property
    def beamsizemmx(self):
        return self.beamsizex * self._conv_scale[self.X]

    @property
    def beamsizemmy(self):
        return self.beamsizey * self._conv_scale[self.Y]

    def _process_image(self):
        image = self._image_raw.copy()
        if self._background_use and self._background.shape == image.shape:
            image -= self._background
            b = _np.where(image < 0)
            image[b] = 0
        else:
            self._background_use = False

        if self._crop_use:
            boo = image > self._crop[self.HIGH]
            image[boo] = self._crop[self.HIGH]
            boo = image < self._crop[self.LOW]
            image[boo] = self._crop[self.LOW]

        self._image_proc = image
        self._update_roi()
        axisx = self._roi_axis[self.X]
        projx = self._roi_proj[self.X]
        axisy = self._roi_axis[self.Y]
        projy = self._roi_proj[self.Y]
        if self._method == self.MOMENTS:
            parx = self._calc_moments(axisx, projx)
            pary = self._calc_moments(axisy, projy)
        else:
            parx = self._fit_gaussian(axisx, projx)
            pary = self._fit_gaussian(axisy, projy)
        self._roi_gauss[self.X] = self._gaussian(axisx, *parx)
        self._roi_gauss[self.Y] = self._gaussian(axisy, *pary)
        self._beam_params[self.X] = parx
        self._beam_params[self.Y] = pary

    def _update_roi(self):
        image = self._image_proc
        axis_x = _np.arange(image.shape[1])
        axis_y = _np.arange(image.shape[0])

        if self._conv_autocenter:
            self._conv_cen[self.X] = image.shape[self.X]//2
            self._conv_cen[self.Y] = image.shape[self.Y]//2

        if self._roi_autocenter:
            proj_x = image.sum(axis=0)
            proj_y = image.sum(axis=1)
            parx = self._calc_moments(axis_x, proj_x)
            pary = self._calc_moments(axis_y, proj_y)
            self._roi_cen[self.X] = int(parx[self.CEN])
            self._roi_cen[self.Y] = int(pary[self.CEN])

        strtx = self._roi_cen[self.X] + self._roi_size[self.X]
        endx = self._roi_cen[self.X] - self._roi_size[self.X]
        strty = self._roi_cen[self.Y] + self._roi_size[self.Y]
        endy = self._roi_cen[self.Y] - self._roi_size[self.Y]
        strtx, strty = max(strtx, 0), max(strty, 0)
        endx, endy = min(endx, image.shape[1]), min(endy, image.shape[0])

        image = image[strty:endy, strtx:endx]
        self._roi_proj[self.X] = image.sum(axis=0)
        self._roi_proj[self.Y] = image.sum(axis=1)
        self._roi_axis[self.X] = axis_x[strtx:endx]
        self._roi_axis[self.Y] = axis_y[strty:endy]
        self._roi_start[self.X] = strtx
        self._roi_start[self.Y] = strty
        self._roi_end[self.X] = endx
        self._roi_end[self.Y] = endy

    @classmethod
    def _calc_moments(cls, axis, proj):
        ret = [0, 0, 0, 0]
        y0 = _np.min(proj)
        proj = proj - y0
        amp = _np.amax(proj)
        dx = axis[1]-axis[0]
        Norm = _np.trapz(proj, dx=dx)
        cen = _np.trapz(proj*axis, dx=dx)/Norm
        sec = _np.trapz(proj*axis*axis, dx=dx)/Norm
        std = _np.sqrt(sec - cen*cen)
        ret[cls.AMP] = amp
        ret[cls.CEN] = cen
        ret[cls.SIG] = std
        ret[cls.OFF] = y0
        return ret

    @classmethod
    def _gaussian(cls, x, *args):
        mu = args[cls.CEN]
        sigma = args[cls.SIG]
        y0 = args[cls.OFF]
        amp = args[cls.AMP]
        x = x - mu
        return amp*_np.exp(-x*x/(2.0*sigma*sigma))+y0

    @classmethod
    def _fit_gaussian(cls, x, y, amp=None, mu=None, sigma=None, y0=None):
        par = cls._calc_moments(x, y)
        par[cls.CEN] = mu or par[cls.CEN]
        par[cls.SIG] = sigma or par[cls.SIG]
        par[cls.OFF] = y0 or par[cls.OFF]
        par[cls.AMP] = amp or par[cls.AMP]
        try:
            par, _ = curve_fit(cls._gaussian, x, y, par)
        except Exception:
            pass
        return par


class CalcEnergy:
    """."""
    DEFAULT_DISP = 1.087
    DEFAULT_B_ANG = _np.pi/4
    DEFAULT_SPECT = 'LI-01:PS-Spect'

    def __init__(self, dispersion=None, angle=None, spectrometer=None):
        """."""
        self._dispersion = dispersion or self.DEFAULT_DISP
        self._angle = angle or self.DEFAULT_B_ANG
        self._spect = spectrometer or self.DEFAULT_SPECT
        self.spect_excdata = _PSS.conv_psname_2_excdata(self._spect)

    @property
    def dispersion(self):
        """."""
        return self._dispersion

    @dispersion.setter
    def dispersion(self, val):
        if isinstance(val, (float, int)) and val != 0:
            self._dispersion = val

    @property
    def angle(self):
        """."""
        return self._angle

    @angle.setter
    def angle(self, val):
        if isinstance(val, (float, int)) and val != 0 and abs(val) < _np.pi:
            self._angle = val

    @property
    def spectrometer(self):
        """."""
        return self._spect

    @spectrometer.setter
    def spectrometer(self, val):
        try:
            self.spect_excdata = _PSS.conv_psname_2_excdata(val)
        except Exception:
            return
        self._spect = val

    def get_integrated_dipole(self, bend_curr):
        """."""
        multipoles = self.spect_excdata.interp_curr2mult(currents=bend_curr)
        return multipoles['normal'][0]

    def get_energy_and_spread(self, bend_curr, cen_x=None, sigma_x=None):
        """."""
        energy = spread = None
        if cen_x is not None:
            BL = self.get_integrated_dipole(bend_curr)
            pc_nom = BL / self._angle * C * 1e-9  # in GeV
            pc = pc_nom * (1 - cen_x / self._dispersion)
            energy = _np.sqrt(pc**2 + E0*E0)
        if sigma_x is None:
            spread = sigma_x / self._dispersion * 100  # in percent%
        return energy, spread


class CalcEmmitance:

    def _perform_analysis(self):
        sigma = np.array(self.sigma)
        I_meas = np.array(self.I_meas)
        pl = self.plane_meas
        K1 = self._get_K1_from_I(I_meas)

        # Transfer Matrix
        nem, bet, alp = self._trans_matrix_analysis(K1, sigma, pl=pl)
        getattr(self, 'nemit' + pl + '_tm').append(nem)
        getattr(self, 'beta' + pl + '_tm').append(bet)
        getattr(self, 'alpha' + pl + '_tm').append(alp)

        # Parabola Fitting
        nem, bet, alp = self._thin_lens_approx(K1, sigma, pl=pl)
        getattr(self, 'nemit' + pl + '_parf').append(nem)
        getattr(self, 'beta' + pl + '_parf').append(bet)
        getattr(self, 'alpha' + pl + '_parf').append(alp)

        for pref in ('nemit', 'beta', 'alpha'):
            for var in ('_tm', '_parf'):
                tp = pref + pl + var
                yd = np.array(getattr(self, tp))
                line = getattr(self, 'line_'+tp)
                line.set_xdata(np.arange(yd.shape[0]))
                line.set_ydata(yd)
                lb = getattr(self, 'lb_'+tp)
                lb.setText('{0:.3f}'.format(yd.mean()))
            params = []
            for var in ('x_tm', 'y_tm', 'x_parf', 'y_parf'):
                params.extend(getattr(self, pref + var))
            params = np.array(params)
            plt = getattr(self, 'plt_' + pref)
            plt.axes.set_xlim([-0.1, params.shape[0]+0.1])
            plt.axes.set_ylim([params.min()*(1-DT), params.max()*(1+DT)])
            plt.figure.canvas.draw()

    def _get_K1_from_I(self, I_meas):
        energy = self.spbox_energy.value() * 1e-3  # energy in GeV
        KL = self.conv2kl.conv_current_2_strength(
                                I_meas, strengths_dipole=energy)
        return KL/self.QUAD_L

    def _trans_matrix_analysis(self, K1, sigma, pl='x'):
        Rx, Ry = self._get_trans_mat(K1)
        R = Rx if pl == 'x' else Ry
        pseudo_inv = (np.linalg.inv(np.transpose(R) @ R) @ np.transpose(R))
        [s_11, s_12, s_22] = pseudo_inv @ (sigma*sigma)
        # s_11, s_12, s_22 = np.linalg.lstsq(R, sigma * sigma)[0]
        nemit, beta, alpha, gamma = self._twiss(s_11, s_12, s_22)
        return nemit, beta, alpha

    def _thin_lens_approx(self, K1, sigma, pl='x'):
        K1 = K1 if pl == 'x' else -K1
        a, b, c = np.polyfit(K1, sigma*sigma, 2)
        yd = np.sqrt(np.polyval([a, b, c], K1))
        self.line_fit.set_xdata(self.I_meas)
        self.line_fit.set_ydata(yd*1e3)
        self.plt_sigma.figure.canvas.draw()

        d = self.DIST + self.QUAD_L/2
        l = self.QUAD_L
        s_11 = a/(d*l)**2
        s_12 = (-b-2*d*l*s_11)/(2*l*d*d)
        s_22 = (c-s_11-2*d*s_12)/d**2
        nemit, beta, alpha, gamma = self._twiss(s_11, s_12, s_22)
        return nemit, beta, alpha

    def _twiss(self, s_11, s_12, s_22):
        energy = self.spbox_energy.value()  # energy in MeV
        emit = np.sqrt(abs(s_11 * s_22 - s_12 * s_12))
        beta = s_11 / emit
        alpha = -s_12 / emit
        gamma = s_22 / emit
        nemit = emit * energy / E0 * 1e6  # in mm.mrad
        return nemit, beta, alpha, gamma

    def _get_trans_mat(self, K1):
        R = np.zeros((len(K1), 4, 4))
        Rd = gettransmat('drift', L=self.DIST)
        for i, k1 in enumerate(K1):
            Rq = gettransmat('quad', L=self.QUAD_L, K1=k1)
            R[i] = np.dot(Rd, Rq)
        R11 = R[:, 0, 0].reshape(-1, 1)
        R12 = R[:, 0, 1].reshape(-1, 1)
        R33 = R[:, 2, 2].reshape(-1, 1)
        R34 = R[:, 2, 3].reshape(-1, 1)
        Rx = np.column_stack((R11*R11, 2*R11*R12, R12*R12))
        Ry = np.column_stack((R33*R33, 2*R33*R34, R34*R34))
        return Rx, Ry
