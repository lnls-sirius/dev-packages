"""."""

from functools import partial as _part
import logging as _log
import numpy as _np
from scipy.optimize import curve_fit

from ..callbacks import Callback

from .csdev import Const as _Const


class BaseClass(Callback, _Const):
    """."""

    def __init__(self, callback=None):
        """."""
        self._map2read = self.get_map2read()
        self._map2write = self.get_map2write()
        super().__init__(callback=callback)

    def get_map2write(self):
        """."""
        return dict()

    def get_map2read(self):
        """."""
        return dict()

    def get(self, prop):
        """."""
        if prop in self._map2read:
            return self._map2read[prop]()
        return self.__getattribute__(prop)

    def read(self, prop):
        """."""
        return self.get(prop)

    def write(self, prop, value):
        """."""
        if prop in self._map2write:
            return self._map2write[prop](value)
        try:
            self.__setattr__(prop, value)
        except Exception:
            return False
        return True


class ProcessImage(BaseClass):
    """."""

    def __init__(self, callback=None):
        """."""
        super().__init__(callback=callback)
        self._roi_autocenter = True
        self._roi_cen = [0, 0]
        self._roi_size = [self.DEFAULT_ROI_SIZE, self.DEFAULT_ROI_SIZE]
        self._roi_start = [0, 0]
        self._roi_end = [0, 0]
        self._roi_axis = [
            _np.arange(self.DEFAULT_ROI_SIZE, dtype=int),
            _np.arange(self.DEFAULT_ROI_SIZE, dtype=int)]
        self._roi_proj = [
            _np.zeros(self.DEFAULT_ROI_SIZE, dtype=float),
            _np.zeros(self.DEFAULT_ROI_SIZE, dtype=float)]
        self._roi_gauss = [
            _np.zeros(self.DEFAULT_ROI_SIZE, dtype=float),
            _np.zeros(self.DEFAULT_ROI_SIZE, dtype=float)]
        self._background = _np.zeros(
            (self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT), dtype=float)
        self._background_use = False
        self._crop = [0, 2**16]
        self._crop_use = False
        self._width = 0
        self._reading_order = self.ReadingOrder.CLike
        self._method = self.Method.GaussFit
        self._nr_averages = 1
        self._images = []
        self._reset_buffer = False
        self._image = _np.zeros(
            (self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT), dtype=float)
        self._conv_autocenter = True
        self._conv_cen = [0, 0]
        self._conv_scale = [1, 1]
        self._flip = [False, False]
        self._beam_params = [None, None]

    def get_map2write(self):
        """."""
        return {
            'ResetBuffer-Cmd': self.cmd_reset_buffer,
            'Image-SP': _part(self.write, 'image'),
            'Width-SP': _part(self.write, 'imagewidth'),
            'ReadingOrder-Sel': _part(self.write, 'readingorder'),
            'NrAverages-SP': _part(self.write, 'nr_averages'),
            'ImgCropLow-SP': _part(self.write, 'imagecroplow'),
            'ImgCropHigh-SP': _part(self.write, 'imagecrophigh'),
            'ImgCropUse-Sel': _part(self.write, 'useimagecrop'),
            'ImgFlipX-Sel': _part(self.write, 'imageflipx'),
            'ImgFlipY-Sel': _part(self.write, 'imageflipy'),
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
        """."""
        return {
            'Image-RB': _part(self.read, 'image'),
            'Width-RB': _part(self.read, 'imagewidth'),
            'ReadingOrder-Sts': _part(self.read, 'readingorder'),
            'NrAverages-RB': _part(self.read, 'nr_averages'),
            'BufferSize-Mon': _part(self.read, 'buffer_size'),
            'ImgCropLow-RB': _part(self.read, 'imagecroplow'),
            'ImgCropHigh-RB': _part(self.read, 'imagecrophigh'),
            'ImgCropUse-Sts': _part(self.read, 'useimagecrop'),
            'ImgFlipX-Sts': _part(self.read, 'imageflipx'),
            'ImgFlipY-Sts': _part(self.read, 'imageflipy'),
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
            'BeamOffsetX-Mon': _part(self.read, 'beamoffsetx'),
            'BeamOffsetY-Mon': _part(self.read, 'beamoffsety'),
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
        """."""
        return self._image.copy().ravel()

    @image.setter
    def image(self, val):
        """."""
        if not isinstance(val, _np.ndarray):
            _log.error('Image is not a numpy array')
            return
        self._process_image(val)

    @property
    def imagewidth(self):
        """."""
        return self._width

    @imagewidth.setter
    def imagewidth(self, val):
        """."""
        if val is None:
            _log.error('could not set width')
            return
        self._width = int(val)
        self.run_callbacks('Width-RB', int(val))
        img = self._adjust_image_dimensions(self._background)
        if img is not None:
            self._background = img
        else:
            _log.error('could not set background')

    @property
    def readingorder(self):
        """."""
        return self._reading_order

    @readingorder.setter
    def readingorder(self, val):
        """."""
        if int(val) in self.ReadingOrder:
            self._reading_order = int(val)
            self.run_callbacks('ReadingOrder-Sts', int(val))

    @property
    def nr_averages(self):
        """Return the number of averages to be used."""
        return self._nr_averages

    @nr_averages.setter
    def nr_averages(self, val):
        self._nr_averages = int(val)
        self.run_callbacks('NrAverages-RB', val)

    @property
    def buffer_size(self):
        """Return the current buffer size."""
        return len(self._images)

    @property
    def imagecroplow(self):
        """."""
        return self._crop[self.CropIdx.Low]

    @imagecroplow.setter
    def imagecroplow(self, val):
        """."""
        val = int(val)
        if 0 <= val < self._crop[self.CropIdx.High]:
            self._crop[self.CropIdx.Low] = val
            self.run_callbacks('ImgCropLow-RB', val)

    @property
    def imagecrophigh(self):
        """."""
        return self._crop[self.CropIdx.High]

    @imagecrophigh.setter
    def imagecrophigh(self, val):
        """."""
        val = int(val)
        if self._crop[self.CropIdx.Low] < val:
            self._crop[self.CropIdx.High] = val
            self.run_callbacks('ImgCropHigh-RB', val)

    @property
    def useimagecrop(self):
        """."""
        return self._crop_use

    @useimagecrop.setter
    def useimagecrop(self, val):
        """."""
        self._crop_use = bool(val)
        self.run_callbacks('ImgCropUse-Sts', int(val))

    @property
    def imageflipx(self):
        """."""
        return self._flip[self.Plane.X]

    @imageflipx.setter
    def imageflipx(self, val):
        """."""
        self._flip[self.Plane.X] = bool(val)
        self.run_callbacks('ImgFlipX-Sts', int(val))

    @property
    def imageflipy(self):
        """."""
        return self._flip[self.Plane.Y]

    @imageflipy.setter
    def imageflipy(self, val):
        """."""
        self._flip[self.Plane.Y] = bool(val)
        self.run_callbacks('ImgFlipY-Sts', int(val))

    @property
    def imagesizex(self):
        """."""
        return self._image.shape[self.Plane.X]

    @property
    def imagesizey(self):
        """."""
        return self._image.shape[self.Plane.Y]

    @property
    def method(self):
        """."""
        return self._method

    @method.setter
    def method(self, val):
        """."""
        if int(val) in self.Method:
            self._method = int(val)
            self.run_callbacks('CalcMethod-Sts', int(val))

    @property
    def roiautocenter(self):
        """."""
        return self._roi_autocenter

    @roiautocenter.setter
    def roiautocenter(self, val):
        """."""
        self._roi_autocenter = bool(val)
        self.run_callbacks('ROIAutoCenter-Sts', int(val))

    @property
    def roicenterx(self):
        """."""
        return self._roi_cen[self.Plane.X]

    @roicenterx.setter
    def roicenterx(self, val):
        """."""
        val = int(val)
        if 0 <= val < self._image.shape[self.Plane.X]:
            self._roi_cen[self.Plane.X] = val
            self.run_callbacks('ROICenterX-RB', val)

    @property
    def roicentery(self):
        """."""
        return self._roi_cen[self.Plane.Y]

    @roicentery.setter
    def roicentery(self, val):
        """."""
        val = int(val)
        if 0 <= val < self._image.shape[self.Plane.Y]:
            self._roi_cen[self.Plane.Y] = val
            self.run_callbacks('ROICenterY-RB', val)

    @property
    def roisizex(self):
        """."""
        return self._roi_size[self.Plane.X]

    @roisizex.setter
    def roisizex(self, val):
        """."""
        val = int(val)
        if 1 <= val < self._image.shape[self.Plane.X]:
            self._roi_size[self.Plane.X] = val
            self.run_callbacks('ROISizeX-RB', val)

    @property
    def roisizey(self):
        """."""
        return self._roi_size[self.Plane.Y]

    @roisizey.setter
    def roisizey(self, val):
        """."""
        val = int(val)
        if 1 <= val < self._image.shape[self.Plane.Y]:
            self._roi_size[self.Plane.Y] = val
            self.run_callbacks('ROISizeY-RB', val)

    @property
    def roistartx(self):
        """."""
        return self._roi_start[self.Plane.X]

    @property
    def roistarty(self):
        """."""
        return self._roi_start[self.Plane.Y]

    @property
    def roiendx(self):
        """."""
        return self._roi_end[self.Plane.X]

    @property
    def roiendy(self):
        """."""
        return self._roi_end[self.Plane.Y]

    @property
    def roiprojx(self):
        """."""
        return self._roi_proj[self.Plane.X].copy()

    @property
    def roiprojy(self):
        """."""
        return self._roi_proj[self.Plane.Y].copy()

    @property
    def roiaxisx(self):
        """."""
        return self._roi_axis[self.Plane.X].copy()

    @property
    def roiaxisy(self):
        """."""
        return self._roi_axis[self.Plane.Y].copy()

    @property
    def roigaussx(self):
        """."""
        return self._roi_gauss[self.Plane.X].copy()

    @property
    def roigaussy(self):
        """."""
        return self._roi_gauss[self.Plane.Y].copy()

    @property
    def background(self):
        """."""
        return self._background.copy().ravel()

    @background.setter
    def background(self, val):
        """."""
        if not isinstance(val, _np.ndarray):
            _log.error('Could not set background')
            return
        img = self._adjust_image_dimensions(np.array(val, dtype=float))
        if img is None:
            _log.error('Could not set background')
            return
        self._background = img
        self.run_callbacks('Background-RB', self.background)

    @property
    def usebackground(self):
        """."""
        return self._background_use

    @usebackground.setter
    def usebackground(self, val):
        """."""
        self._background_use = bool(val)
        self.run_callbacks('BgUse-Sts', val)

    @property
    def beamcenterx(self):
        """."""
        return self._beam_params[self.Plane.X][self.FitParams.Cen]

    @property
    def beamcentery(self):
        """."""
        return self._beam_params[self.Plane.Y][self.FitParams.Cen]

    @property
    def beamsizex(self):
        """."""
        return abs(self._beam_params[self.Plane.X][self.FitParams.Sig])

    @property
    def beamsizey(self):
        """."""
        return abs(self._beam_params[self.Plane.Y][self.FitParams.Sig])

    @property
    def beamamplx(self):
        """."""
        return self._beam_params[self.Plane.X][self.FitParams.Amp]

    @property
    def beamamply(self):
        """."""
        return self._beam_params[self.Plane.Y][self.FitParams.Amp]

    @property
    def beamoffsetx(self):
        """."""
        return self._beam_params[self.Plane.X][self.FitParams.Off]

    @property
    def beamoffsety(self):
        """."""
        return self._beam_params[self.Plane.Y][self.FitParams.Off]

    @property
    def px2mmscalex(self):
        """."""
        return self._conv_scale[self.Plane.X]

    @px2mmscalex.setter
    def px2mmscalex(self, val):
        """."""
        if val != 0:
            self._conv_scale[self.Plane.X] = val
            self.run_callbacks('Px2mmScaleX-RB', val)
        else:
            _log.error('Could not set px2mmscaley')

    @property
    def px2mmscaley(self):
        """."""
        return self._conv_scale[self.Plane.Y]

    @px2mmscaley.setter
    def px2mmscaley(self, val):
        """."""
        if val != 0:
            self._conv_scale[self.Plane.Y] = val
            self.run_callbacks('Px2mmScaleY-RB', val)
        else:
            _log.error('Could not set px2mmscaley')

    @property
    def px2mmautocenter(self):
        """."""
        return self._conv_autocenter

    @px2mmautocenter.setter
    def px2mmautocenter(self, val):
        """."""
        self._conv_autocenter = bool(val)
        self.run_callbacks('Px2mmAutoCenter-Sts', val)

    @property
    def px2mmcenterx(self):
        """."""
        return self._conv_cen[self.Plane.X]

    @px2mmcenterx.setter
    def px2mmcenterx(self, val):
        """."""
        val = int(val)
        if 0 <= val < self._image.shape[self.Plane.X]:
            self._conv_cen[self.Plane.X] = val
            self.run_callbacks('Px2mmCenterX-RB', val)
        else:
            _log.error('Could not set px2mmcenterx')

    @property
    def px2mmcentery(self):
        """."""
        return self._conv_cen[self.Plane.Y]

    @px2mmcentery.setter
    def px2mmcentery(self, val):
        """."""
        val = int(val)
        if 0 <= val < self._image.shape[self.Plane.Y]:
            self._conv_cen[self.Plane.Y] = val
            self.run_callbacks('Px2mmCenterY-RB', val)
        else:
            _log.error('Could not set px2mmcentery')

    @property
    def beamcentermmx(self):
        """."""
        val = self.beamcenterx - self._conv_cen[self.Plane.X]
        val *= self._conv_scale[self.Plane.X]
        return val

    @property
    def beamcentermmy(self):
        """."""
        # Inverted due image origin in Pxls:
        val = self._conv_cen[self.Plane.Y] - self.beamcentery
        val *= self._conv_scale[self.Plane.Y]
        return val

    @property
    def beamsizemmx(self):
        """."""
        return self.beamsizex * self._conv_scale[self.Plane.X]

    @property
    def beamsizemmy(self):
        """."""
        return self.beamsizey * self._conv_scale[self.Plane.Y]

    def cmd_reset_buffer(self, *args):
        """Schedule reset Buffer in next update."""
        _ = args
        self._reset_buffer = True
        self.run_callbacks('BufferSize-Mon', 0)

    def _process_image(self, image):
        """."""
        image = self._adjust_image_dimensions(image)
        image = _np.array(image, dtype=float)
        if image is None:
            _log.error('Image is None')
            return

        # check whether to reset or not the buffer
        imgs = self._images
        self._reset_buffer |= bool(imgs) and (imgs[-1].shape != image.shape)
        if self._reset_buffer:
            self._images = [image, ]
            self._reset_buffer = False
        else:
            self._images.append(image)
            self._images = self._images[-self._nr_averages:]
        buf_size = self.buffer_size
        self.run_callbacks('BufferSize-Mon', buf_size)

        # calculate average of the images
        if buf_size > 1:
            image = self._images[0].copy()
            for img in self._images[1:]:  # faster than using numpy.mean
                image += img
            image /= len(self._images)

        if self._background_use and self._background.shape == image.shape:
            image -= self._background
            b = _np.where(image < 0)
            image[b] = 0
        else:
            self.usebackground = False

        if self._crop_use:
            boo = image > self._crop[self.CropIdx.High]
            image[boo] = self._crop[self.CropIdx.High]
            boo = image < self._crop[self.CropIdx.Low]
            image[boo] = self._crop[self.CropIdx.Low]

        if self._flip[self.Plane.X]:
            image = _np.flip(image, axis=self.Plane.X)
        if self._flip[self.Plane.Y]:
            image = _np.flip(image, axis=self.Plane.Y)

        self._image = image
        self.run_callbacks('Image-RB', self.image)
        self._update_roi()
        axisx = self._roi_axis[self.Plane.X]
        projx = self._roi_proj[self.Plane.X]
        axisy = self._roi_axis[self.Plane.Y]
        projy = self._roi_proj[self.Plane.Y]
        if self._method == self.Method.Moments:
            parx = self._calc_moments(axisx, projx)
            pary = self._calc_moments(axisy, projy)
        else:
            parx = self._fit_gaussian(
                axisx, projx, self._beam_params[self.Plane.X])
            pary = self._fit_gaussian(
                axisy, projy, self._beam_params[self.Plane.Y])
        self._roi_gauss[self.Plane.X] = self._gaussian(axisx, *parx)
        self._roi_gauss[self.Plane.Y] = self._gaussian(axisy, *pary)
        self._beam_params[self.Plane.X] = parx
        self._beam_params[self.Plane.Y] = pary
        self.run_callbacks('ROIGaussFitX-Mon', self._roi_gauss[self.Plane.X])
        self.run_callbacks('ROIGaussFitY-Mon', self._roi_gauss[self.Plane.Y])
        self.run_callbacks('BeamCenterX-Mon', self.beamcenterx)
        self.run_callbacks('BeamCenterY-Mon', self.beamcentery)
        self.run_callbacks('BeamSizeX-Mon', self.beamsizex)
        self.run_callbacks('BeamSizeY-Mon', self.beamsizey)
        self.run_callbacks('BeamCentermmX-Mon', self.beamcentermmx)
        self.run_callbacks('BeamCentermmY-Mon', self.beamcentermmy)
        self.run_callbacks('BeamSizemmX-Mon', self.beamsizemmx)
        self.run_callbacks('BeamSizemmY-Mon', self.beamsizemmy)
        self.run_callbacks('BeamAmplX-Mon', self.beamamplx)
        self.run_callbacks('BeamAmplY-Mon', self.beamamply)
        self.run_callbacks('BeamOffsetX-Mon', self.beamoffsetx)
        self.run_callbacks('BeamOffsetY-Mon', self.beamoffsety)

    def _adjust_image_dimensions(self, img):
        """."""
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
        """."""
        image = self._image
        axis_x = _np.arange(image.shape[self.Plane.X])
        axis_y = _np.arange(image.shape[self.Plane.Y])

        if self._conv_autocenter:
            self.px2mmcenterx = image.shape[self.Plane.X]//2
            self.px2mmcentery = image.shape[self.Plane.Y]//2

        if self._roi_autocenter:
            proj_x = image.sum(axis=0)
            proj_y = image.sum(axis=1)
            parx = self._calc_moments(axis_x, proj_x)
            pary = self._calc_moments(axis_y, proj_y)
            if not any(_np.isnan(parx+pary)):
                self.roicenterx = int(parx[self.FitParams.Cen])
                self.roicentery = int(pary[self.FitParams.Cen])
            else:
                _log.error('Some fitted params are NaN.')

        strtx = self._roi_cen[self.Plane.X] - self._roi_size[self.Plane.X]
        endx = self._roi_cen[self.Plane.X] + self._roi_size[self.Plane.X]
        strty = self._roi_cen[self.Plane.Y] - self._roi_size[self.Plane.Y]
        endy = self._roi_cen[self.Plane.Y] + self._roi_size[self.Plane.Y]
        strtx, strty = max(strtx, 0), max(strty, 0)
        endx = min(endx, image.shape[self.Plane.X])
        endy = min(endy, image.shape[self.Plane.Y])

        image = image[strty:endy, strtx:endx]
        self._roi_proj[self.Plane.X] = image.sum(axis=self.Plane.Y)
        self._roi_proj[self.Plane.Y] = image.sum(axis=self.Plane.X)
        self._roi_axis[self.Plane.X] = axis_x[strtx:endx]
        self._roi_axis[self.Plane.Y] = axis_y[strty:endy]
        self._roi_start[self.Plane.X] = strtx
        self._roi_start[self.Plane.Y] = strty
        self._roi_end[self.Plane.X] = endx
        self._roi_end[self.Plane.Y] = endy
        self.run_callbacks('ROIProjX-Mon', self._roi_proj[self.Plane.X])
        self.run_callbacks('ROIProjY-Mon', self._roi_proj[self.Plane.Y])
        self.run_callbacks('ROIAxisX-Mon', self._roi_axis[self.Plane.X])
        self.run_callbacks('ROIAxisY-Mon', self._roi_axis[self.Plane.Y])
        self.run_callbacks('ROIStartX-Mon', self._roi_start[self.Plane.X])
        self.run_callbacks('ROIStartY-Mon', self._roi_start[self.Plane.Y])
        self.run_callbacks('ROIEndX-Mon', self._roi_end[self.Plane.X])
        self.run_callbacks('ROIEndY-Mon', self._roi_end[self.Plane.Y])

    @classmethod
    def _calc_moments(cls, axis, proj):
        """."""
        ret = [0, 0, 0, 0]
        y0 = _np.min(proj)
        proj = proj - y0
        amp = _np.amax(proj)
        dx = axis[1]-axis[0]
        norm = _np.trapz(proj, dx=dx)
        praxis = proj*axis
        cen = _np.trapz(praxis, dx=dx)/norm
        sec = _np.trapz(praxis*axis, dx=dx)/norm
        std = _np.sqrt(sec - cen*cen)
        ret[cls.FitParams.Amp] = amp
        ret[cls.FitParams.Cen] = cen
        ret[cls.FitParams.Sig] = std
        ret[cls.FitParams.Off] = y0
        return ret

    @classmethod
    def _gaussian(cls, x, *args):
        """."""
        mu = args[cls.FitParams.Cen]
        sigma = args[cls.FitParams.Sig]
        y0 = args[cls.FitParams.Off]
        amp = args[cls.FitParams.Amp]
        x = x - mu
        return amp*_np.exp(-x*x/(2.0*sigma*sigma))+y0

    @classmethod
    def _fit_gaussian(cls, x, y, par=None):
        """."""
        if par is None:
            par = cls._calc_moments(x, y)
        try:
            par, _ = curve_fit(cls._gaussian, x, y, par)
        except Exception:
            _log.error('Could not fit gaussian.')
        return par
