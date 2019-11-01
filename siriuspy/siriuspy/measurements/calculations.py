
from functools import partial as _part
from copy import deepcopy as _dcopy
import logging as _log
import numpy as _np
from scipy.optimize import curve_fit
from siriuspy.search import PSSearch as _PSS
import mathphys.constants as _consts
from siriuspy.factory import NormalizerFactory as _NormFact
from .base import BaseClass as _BaseClass

C = _consts.light_speed
E0 = _consts.electron_rest_energy / _consts.elementary_charge * 1e-9  # in GeV


class ProcessImage(_BaseClass):

    def __init__(self):
        super().__init__()
        self._roi_autocenter = True
        self._roi_cen = [0, 0]
        self._roi_size = [self.DEFAULT_ROI_SIZE, self.DEFAULT_ROI_SIZE]
        self._roi_start = [0, 0]
        self._roi_end = [0, 0]
        self._roi_axis = [
            _np.arange(self.DEFAULT_ROI_SIZE, dtype=int),
            _np.arange(self.DEFAULT_ROI_SIZE, dtype=int)]
        self._roi_proj = [
            _np.zeros(self.DEFAULT_ROI_SIZE, dtype=int),
            _np.zeros(self.DEFAULT_ROI_SIZE, dtype=int)]
        self._roi_gauss = [
            _np.zeros(self.DEFAULT_ROI_SIZE, dtype=float),
            _np.zeros(self.DEFAULT_ROI_SIZE, dtype=float)]
        self._background = _np.zeros(
            (self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT), dtype=int)
        self._background_use = False
        self._crop = [0, 255]
        self._crop_use = False
        self._width = 0
        self._reading_order = self.ReadingOrder.CLike
        self._method = self.Method.GaussFit
        self._image = _np.zeros(
            (self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT), dtype=int)
        self._conv_autocenter = True
        self._conv_cen = [0, 0]
        self._conv_scale = [1, 1]
        self._beam_params = [[0, 1, 1, 0], [0, 1, 1, 0]]

    def get_map2write(self):
        return {
            'Image-SP': _part(self.write, 'image'),
            'Width-SP': _part(self.write, 'imagewidth'),
            'ReadingOrder-Sel': _part(self.write, 'readingorder'),
            'ImgCropLow-SP': _part(self.write, 'imagecroplow'),
            'ImgCropHigh-SP': _part(self.write, 'imagecrophigh'),
            'ImgCropUse-Sel': _part(self.write, 'useimagecrop'),
            'CalcMethod-Sel': _part(self.write, 'method'),
            'ROIAutoCenter-Sel': _part(self.write, 'roiautocenter'),
            'ROICenterX-SP': _part(self.write, 'roicenterx'),
            'ROICenterY-SP': _part(self.write, 'roicentery'),
            'ROISizeX-SP': _part(self.write, 'roisizex'),
            'ROISizeY-SP': _part(self.write, 'roisizey'),
            'Background-SP': _part(self.write, 'background'),
            'BgUse-Sel': _part(self.write, 'usebackground'),
            'Px2mmScaleX-SP': _part(self.write, 'px2mmscalex'),
            'Px2mmScaleY-SP': _part(self.write, 'px2mmscaley'),
            'Px2mmAutoCenter-Sel': _part(self.write, 'px2mmautocenter'),
            'Px2mmCenterX-SP': _part(self.write, 'px2mmcenterx'),
            'Px2mmCenterY-SP': _part(self.write, 'px2mmcentery'),
            }

    def get_map2read(self):
        return {
            'Image-RB': _part(self.read, 'image'),
            'Width-RB': _part(self.read, 'imagewidth'),
            'ReadingOrder-Sts': _part(self.read, 'readingorder'),
            'ImgCropLow-RB': _part(self.read, 'imagecroplow'),
            'ImgCropHigh-RB': _part(self.read, 'imagecrophigh'),
            'ImgCropUse-Sts': _part(self.read, 'useimagecrop'),
            'CalcMethod-Sts': _part(self.read, 'method'),
            'ROIAutoCenter-Sts': _part(self.read, 'roiautocenter'),
            'ROICenterX-RB': _part(self.read, 'roicenterx'),
            'ROICenterY-RB': _part(self.read, 'roicentery'),
            'ROISizeX-RB': _part(self.read, 'roisizex'),
            'ROISizeY-RB': _part(self.read, 'roisizey'),
            'ROIStartX-Mon': _part(self.read, 'roistartx'),
            'ROIStartY-Mon': _part(self.read, 'roistarty'),
            'ROIEndX-Mon': _part(self.read, 'roiendx'),
            'ROIEndY-Mon': _part(self.read, 'roiendy'),
            'ROIProjX-Mon': _part(self.read, 'roiprojx'),
            'ROIProjY-Mon': _part(self.read, 'roiprojy'),
            'ROIAxisX-Mon': _part(self.read, 'roiaxisx'),
            'ROIAxisY-Mon': _part(self.read, 'roiaxisy'),
            'ROIGaussFitX-Mon': _part(self.read, 'roigaussx'),
            'ROIGaussFitY-Mon': _part(self.read, 'roigaussy'),
            'BeamCenterX-Mon': _part(self.read, 'beamcenterx'),
            'BeamCenterY-Mon': _part(self.read, 'beamcentery'),
            'BeamSizeX-Mon': _part(self.read, 'beamsizex'),
            'BeamSizeY-Mon': _part(self.read, 'beamsizey'),
            'BeamCentermmX-Mon': _part(self.read, 'beamcentermmx'),
            'BeamCentermmY-Mon': _part(self.read, 'beamcentermmy'),
            'BeamSizemmX-Mon': _part(self.read, 'beamsizemmx'),
            'BeamSizemmY-Mon': _part(self.read, 'beamsizemmy'),
            'BeamAmplX-Mon': _part(self.read, 'beamamplx'),
            'BeamAmplY-Mon': _part(self.read, 'beamamply'),
            'BgOffsetX-Mon': _part(self.read, 'bgoffsetx'),
            'BgOffsetY-Mon': _part(self.read, 'bgoffsety'),
            'Background-RB': _part(self.read, 'background'),
            'BgUse-Sts': _part(self.read, 'usebackground'),
            'Px2mmScaleX-RB': _part(self.read, 'px2mmscalex'),
            'Px2mmScaleY-RB': _part(self.read, 'px2mmscaley'),
            'Px2mmAutoCenter-Sts': _part(self.read, 'px2mmautocenter'),
            'Px2mmCenterX-RB': _part(self.read, 'px2mmcenterx'),
            'Px2mmCenterY-RB': _part(self.read, 'px2mmcentery'),
            }

    @property
    def image(self):
        return self._image.copy().flatten()

    @image.setter
    def image(self, val):
        if not isinstance(val, _np.ndarray):
            _log.error('Image is not a numpy array')
            return
        self._process_image(val)

    @property
    def imagewidth(self):
        return self._width

    @imagewidth.setter
    def imagewidth(self, val):
        if val is None or int(val) == self._width:
            _log.error('could not set width')
            return
        self._width = int(val)
        img = self._adjust_image_dimensions(self._background)
        if img is not None:
            self._background = img
        else:
            _log.error('could not set background')

    @property
    def readingorder(self):
        return self._reading_order

    @readingorder.setter
    def readingorder(self, val):
        if int(val) in self.ReadingOrder:
            self._reading_order = int(val)

    @property
    def imagecroplow(self):
        return self._crop[self.CropIdx.Low]

    @imagecroplow.setter
    def imagecroplow(self, val):
        val = int(val)
        if 0 <= val < self._crop[self.CropIdx.High]:
            self._crop[self.CropIdx.Low] = val

    @property
    def imagecrophigh(self):
        return self._crop[self.CropIdx.High]

    @imagecrophigh.setter
    def imagecrophigh(self, val):
        val = int(val)
        if self._crop[self.CropIdx.Low] < val:
            self._crop[self.CropIdx.High] = val

    @property
    def useimagecrop(self):
        return self._crop_use

    @useimagecrop.setter
    def useimagecrop(self, val):
        self._crop_use = bool(val)

    @property
    def imagesizex(self):
        return self._image.shape[self.Plane.X]

    @property
    def imagesizey(self):
        return self._image.shape[self.Plane.Y]

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, val):
        if int(val) in self.Method:
            self._method = int(val)

    @property
    def roiautocenter(self):
        return self._roi_autocenter

    @roiautocenter.setter
    def roiautocenter(self, val):
        self._roi_autocenter = bool(val)

    @property
    def roicenterx(self):
        return self._roi_cen[self.Plane.X]

    @roicenterx.setter
    def roicenterx(self, val):
        if self._roi_autocenter:
            return
        val = int(val)
        if 0 <= val < self._image.shape[self.Plane.X]:
            self._roi_cen[self.Plane.X] = val

    @property
    def roicentery(self):
        return self._roi_cen[self.Plane.Y]

    @roicentery.setter
    def roicentery(self, val):
        if self._roi_autocenter:
            return
        val = int(val)
        if 0 <= val < self._image.shape[self.Plane.Y]:
            self._roi_cen[self.Plane.Y] = val

    @property
    def roisizex(self):
        return self._roi_size[self.Plane.X]

    @roisizex.setter
    def roisizex(self, val):
        val = int(val)
        if 1 <= val < self._image.shape[self.Plane.X]:
            self._roi_size[self.Plane.X] = val

    @property
    def roisizey(self):
        return self._roi_size[self.Plane.Y]

    @roisizey.setter
    def roisizey(self, val):
        val = int(val)
        if 1 <= val < self._image.shape[self.Plane.Y]:
            self._roi_size[self.Plane.Y] = val

    @property
    def roistartx(self):
        return self._roi_start[self.Plane.X]

    @property
    def roistarty(self):
        return self._roi_start[self.Plane.Y]

    @property
    def roiendx(self):
        return self._roi_end[self.Plane.X]

    @property
    def roiendy(self):
        return self._roi_end[self.Plane.Y]

    @property
    def roiprojx(self):
        return self._roi_proj[self.Plane.X].copy()

    @property
    def roiprojy(self):
        return self._roi_proj[self.Plane.Y].copy()

    @property
    def roiaxisx(self):
        return self._roi_axis[self.Plane.X].copy()

    @property
    def roiaxisy(self):
        return self._roi_axis[self.Plane.Y].copy()

    @property
    def roigaussx(self):
        return self._roi_gauss[self.Plane.X].copy()

    @property
    def roigaussy(self):
        return self._roi_gauss[self.Plane.Y].copy()

    @property
    def background(self):
        return self._background.copy().flatten()

    @background.setter
    def background(self, val):
        if not isinstance(val, _np.ndarray):
            _log.error('Could not set background')
            return
        img = self._adjust_image_dimensions(val.copy())
        if img is None:
            _log.error('Could not set background')
            return
        self._background = img

    @property
    def usebackground(self):
        return self._background_use

    @usebackground.setter
    def usebackground(self, val):
        self._background_use = bool(val)

    @property
    def beamcenterx(self):
        return self._beam_params[self.Plane.X][self.FitParams.Cen]

    @property
    def beamcentery(self):
        return self._beam_params[self.Plane.Y][self.FitParams.Cen]

    @property
    def beamsizex(self):
        return self._beam_params[self.Plane.X][self.FitParams.Sig]

    @property
    def beamsizey(self):
        return self._beam_params[self.Plane.Y][self.FitParams.Sig]

    @property
    def beamamplx(self):
        return self._beam_params[self.Plane.X][self.FitParams.Amp]

    @property
    def beamamply(self):
        return self._beam_params[self.Plane.Y][self.FitParams.Amp]

    @property
    def bgoffsetx(self):
        return self._beam_params[self.Plane.X][self.FitParams.Off]

    @property
    def bgoffsety(self):
        return self._beam_params[self.Plane.Y][self.FitParams.Off]

    @property
    def px2mmscalex(self):
        return self._conv_scale[self.Plane.X]

    @px2mmscalex.setter
    def px2mmscalex(self, val):
        if val != 0:
            self._conv_scale[self.Plane.X] = val
        else:
            _log.error('Could not set px2mmscaley')

    @property
    def px2mmscaley(self):
        return self._conv_scale[self.Plane.Y]

    @px2mmscaley.setter
    def px2mmscaley(self, val):
        if val != 0:
            self._conv_scale[self.Plane.Y] = val
        else:
            _log.error('Could not set px2mmscaley')

    @property
    def px2mmautocenter(self):
        return self._conv_autocenter

    @px2mmautocenter.setter
    def px2mmautocenter(self, val):
        self._conv_autocenter = bool(val)

    @property
    def px2mmcenterx(self):
        return self._conv_cen[self.Plane.X]

    @px2mmcenterx.setter
    def px2mmcenterx(self, val):
        if self._conv_autocenter:
            _log.error('Could not set px2mmcenterx')
            return
        val = int(val)
        if 0 <= val < self._image.shape[self.Plane.Y]:
            self._conv_cen[self.Plane.X] = val
        else:
            _log.error('Could not set px2mmcenterx')

    @property
    def px2mmcentery(self):
        return self._conv_cen[self.Plane.Y]

    @px2mmcentery.setter
    def px2mmcentery(self, val):
        if self._conv_autocenter:
            _log.error('Could not set px2mmcentery')
            return
        val = int(val)
        if 0 <= val < self._image.shape[self.Plane.Y]:
            self._conv_cen[self.Plane.Y] = val
        else:
            _log.error('Could not set px2mmcentery')

    @property
    def beamcentermmx(self):
        val = self.beamcenterx - self._conv_cen[self.Plane.X]
        val *= self._conv_scale[self.Plane.X]
        return val

    @property
    def beamcentermmy(self):
        val = self.beamcentery - self._conv_cen[self.Plane.Y]
        val *= self._conv_scale[self.Plane.Y]
        return val

    @property
    def beamsizemmx(self):
        return self.beamsizex * self._conv_scale[self.Plane.X]

    @property
    def beamsizemmy(self):
        return self.beamsizey * self._conv_scale[self.Plane.Y]

    def _process_image(self, image):
        image = self._adjust_image_dimensions(image.copy())
        if image is None:
            _log.error('Image is None')
            return
        if self._background_use and self._background.shape == image.shape:
            image -= self._background
            b = _np.where(image < 0)
            image[b] = 0
        else:
            self._background_use = False

        if self._crop_use:
            boo = image > self._crop[self.CropIdx.High]
            image[boo] = self._crop[self.CropIdx.High]
            boo = image < self._crop[self.CropIdx.Low]
            image[boo] = self._crop[self.CropIdx.Low]

        self._image = image
        self._update_roi()
        axisx = self._roi_axis[self.Plane.X]
        projx = self._roi_proj[self.Plane.X]
        axisy = self._roi_axis[self.Plane.Y]
        projy = self._roi_proj[self.Plane.Y]
        if self._method == self.Method.Moments:
            parx = self._calc_moments(axisx, projx)
            pary = self._calc_moments(axisy, projy)
        else:
            parx = self._fit_gaussian(axisx, projx)
            pary = self._fit_gaussian(axisy, projy)
        self._roi_gauss[self.Plane.X] = self._gaussian(axisx, *parx)
        self._roi_gauss[self.Plane.Y] = self._gaussian(axisy, *pary)
        self._beam_params[self.Plane.X] = parx
        self._beam_params[self.Plane.Y] = pary

    def _adjust_image_dimensions(self, img):
        if len(img.shape) == 1:
            if self._width <= 1:
                _log.error('Invalid value for Width.')
                return None
            try:
                if self._reading_order == self.ReadingOrder.CLike:
                    img = img.reshape((-1, self._width), order='C')
                else:
                    img = img.reshape((self._width, -1), order='F')
            except ValueError:
                _log.error('Problem reshaping image.')
                return None
        return img

    def _update_roi(self):
        image = self._image
        axis_x = _np.arange(image.shape[1])
        axis_y = _np.arange(image.shape[0])

        if self._conv_autocenter:
            self._conv_cen[self.Plane.X] = image.shape[self.Plane.X]//2
            self._conv_cen[self.Plane.Y] = image.shape[self.Plane.Y]//2

        if self._roi_autocenter:
            proj_x = image.sum(axis=0)
            proj_y = image.sum(axis=1)
            parx = self._calc_moments(axis_x, proj_x)
            pary = self._calc_moments(axis_y, proj_y)
            if not any(_np.isnan(parx+pary)):
                self._roi_cen[self.Plane.X] = int(parx[self.FitParams.Cen])
                self._roi_cen[self.Plane.Y] = int(pary[self.FitParams.Cen])
            else:
                _log.error('Some fitted params are NaN.')

        strtx = self._roi_cen[self.Plane.X] - self._roi_size[self.Plane.X]
        endx = self._roi_cen[self.Plane.X] + self._roi_size[self.Plane.X]
        strty = self._roi_cen[self.Plane.Y] - self._roi_size[self.Plane.Y]
        endy = self._roi_cen[self.Plane.Y] + self._roi_size[self.Plane.Y]
        strtx, strty = max(strtx, 0), max(strty, 0)
        endx, endy = min(endx, image.shape[1]), min(endy, image.shape[0])

        image = image[strty:endy, strtx:endx]
        self._roi_proj[self.Plane.X] = image.sum(axis=0)
        self._roi_proj[self.Plane.Y] = image.sum(axis=1)
        self._roi_axis[self.Plane.X] = axis_x[strtx:endx]
        self._roi_axis[self.Plane.Y] = axis_y[strty:endy]
        self._roi_start[self.Plane.X] = strtx
        self._roi_start[self.Plane.Y] = strty
        self._roi_end[self.Plane.X] = endx
        self._roi_end[self.Plane.Y] = endy

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
        ret[cls.FitParams.Amp] = amp
        ret[cls.FitParams.Cen] = cen
        ret[cls.FitParams.Sig] = std
        ret[cls.FitParams.Off] = y0
        return ret

    @classmethod
    def _gaussian(cls, x, *args):
        mu = args[cls.FitParams.Cen]
        sigma = args[cls.FitParams.Sig]
        y0 = args[cls.FitParams.Off]
        amp = args[cls.FitParams.Amp]
        x = x - mu
        return amp*_np.exp(-x*x/(2.0*sigma*sigma))+y0

    @classmethod
    def _fit_gaussian(cls, x, y, amp=None, mu=None, sigma=None, y0=None):
        par = cls._calc_moments(x, y)
        par[cls.FitParams.Cen] = mu or par[cls.FitParams.Cen]
        par[cls.FitParams.Sig] = sigma or par[cls.FitParams.Sig]
        par[cls.FitParams.Off] = y0 or par[cls.FitParams.Off]
        par[cls.FitParams.Amp] = amp or par[cls.FitParams.Amp]
        try:
            par, _ = curve_fit(cls._gaussian, x, y, par)
        except Exception:
            _log.error('Could not fit gaussian.')
            pass
        return par


class CalcEnergy(_BaseClass):
    """."""

    def __init__(self, dispersion=None, angle=None, spectrometer=None):
        """."""
        super().__init__()
        self._dispersion = dispersion or self.DEFAULT_DISP
        self._angle = angle or self.DEFAULT_B_ANG
        self._spect = spectrometer or self.DEFAULT_SPECT
        self._excdata = _PSS.conv_psname_2_excdata(self._spect)
        self._currents = _np.array([], dtype=float)
        self._intdipole = _np.array([], dtype=float)
        self._energy = _np.array([], dtype=float)
        self._spread = _np.array([], dtype=float)
        self._beamcenter = _np.array([], dtype=float)
        self._beamsize = _np.array([], dtype=float)

    def get_map2write(self):
        return {
            'Dispersion-SP': _part(self.write, 'dispersion'),
            'Angle-SP': _part(self.write, 'angle'),
            'Spectrometer-SP': _part(self.write, 'spectrometer'),
            }

    def get_map2read(self):
        return {
            'Dispersion-RB': _part(self.read, 'dispersion'),
            'Angle-RB': _part(self.read, 'angle'),
            'Spectrometer-RB': _part(self.read, 'spectrometer'),
            'IntDipole-Mon': _part(self.read, 'intdipole'),
            'Energy-Mon': _part(self.read, 'energy'),
            'Spread-Mon': _part(self.read, 'spread'),
            }

    @property
    def dispersion(self):
        """."""
        return self._dispersion

    @dispersion.setter
    def dispersion(self, val):
        if isinstance(val, (float, int)) and val != 0:
            self._dispersion = val
        self._perform_analysis()

    @property
    def angle(self):
        """."""
        return self._angle

    @angle.setter
    def angle(self, val):
        if isinstance(val, (float, int)) and val != 0 and abs(val) < _np.pi:
            self._angle = val
            self._perform_analysis()

    @property
    def spectrometer(self):
        """."""
        return self._spect

    @spectrometer.setter
    def spectrometer(self, val):
        try:
            self._excdata = _PSS.conv_psname_2_excdata(val)
        except Exception:
            return
        self._spect = val
        self._perform_analysis()

    @property
    def currents(self):
        return _dcopy(self._currents)

    @property
    def beamsize(self):
        return _dcopy(self._beamsize)

    @property
    def beamcenter(self):
        return _dcopy(self._beamcenter)

    @property
    def intdipole(self):
        return _dcopy(self._intdipole)

    @property
    def energy(self):
        return _dcopy(self._energy)

    @property
    def spread(self):
        return _dcopy(self._spread)

    def set_data(self, currents, beam_centers, beam_sizes):
        if None in {currents, beam_centers, beam_sizes}:
            return False
        if isinstance(beam_sizes, (int, float)):
            beam_sizes = [beam_sizes]
        if isinstance(beam_centers, (int, float)):
            beam_centers = [beam_centers]
        if isinstance(currents, (int, float)):
            currents = [currents]
        beam_sizes = _np.array(beam_sizes, dtype=float)
        beam_centers = _np.array(beam_centers, dtype=float)
        currents = _np.array(currents, dtype=float)
        cond = beam_sizes.size != currents.size
        cond |= currents.size != beam_centers.size
        if cond:
            return False
        self._beamsize = beam_sizes
        self._beamcenter = beam_centers
        self._currents = currents
        self._perform_analysis()
        return True

    def _update_integrated_dipole(self):
        """."""
        if self._currents.size == 0:
            return
        mult = self._excdata.interp_curr2mult(currents=self._currents)
        self._intdipole = mult['normal'][0]

    def _perform_analysis(self):
        """."""
        self._update_integrated_dipole()
        cond = self._intdipole.size == 0
        cond |= self._beamcenter.size == 0
        cond |= self._beamsize == 0
        if cond:
            return
        pc_nom = self._intdipole / self._angle * C * 1e-9  # in GeV
        pc = pc_nom * (1 - self._beamcenter / self._dispersion)
        self._energy = _np.sqrt(pc**2 + E0*E0)
        self._spread = self._beamsize / self._dispersion * 100  # in percent%


class CalcEmmitance(_BaseClass):
    X = 0
    Y = 1
    PLACES = ('li', 'tb-qd2a', 'tb-qf2a')

    def __init__(self):
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
        return {
            'Place-Sel': _part(self.write, 'place'),
            'Plane-Sel': _part(self.write, 'plane'),
            }

    def get_map2read(self):
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
        if int(val) in self.Plane:
            self._plane = int(val)
        self._perform_analysis()

    @property
    def plane_str(self):
        return self.Plane._fields[self._plane]

    @plane_str.setter
    def plane_str(self, val):
        if val in self.Plane._fields:
            self.plane = self.Plane._fields.index(val)

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
        if not self._beamsize.size:
            return
        self._update_quad_strength()
        self._trans_matrix_analysis()
        self._thin_lens_approx()

    def _update_quad_strength(self):
        KL = self._conv2kl.conv_current_2_strength(
            self._currents, strengths_dipole=self._energy)
        self._quadstren = KL/self._quadlen
        if self._plane == self.Plane.Y:
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
