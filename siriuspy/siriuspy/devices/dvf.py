"""DVF devices."""

import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple
from mathphys.imgproc import Image2D_Fit as _Image2D_Fit
from mathphys.imgproc import FitGaussianScipy as _FitGaussianScipy

from .device import DeviceNC as _DeviceNC


class DVF(_DeviceNC):
    """Beam Visualization Device ("Dispositivo de Visualização de Feixe")."""

    class DEVICES:
        """Devices names."""
        CAX_DVF1 = 'CAX:A:BASLER01'
        CAX_DVF2 = 'CAX:B:BASLER01'
        ALL = (CAX_DVF1, CAX_DVF2)

    _default_timeout = 10  # [s]

    _dvfparam_fields = (
        'MAX_INTENSITY_NR_BITS',
        'ACQUISITION_TIME_MIN',  # [s]
        'ACQUISITION_TIME_DEFAULT',  # [s]
        'EXPOSURE_TIME_DEFAULT',  # [s]
        'IMAGE_SIZE_Y',  # [pixel]
        'IMAGE_SIZE_X',  # [pixel]
        'IMAGE_PIXEL_SIZE',  # [um]
        'OPTICS_MAGNIFICATION_FACTOR',  # source to image
    )
    #   DVF device :       ((sizey, sizex), pixel_size_um mag_factor
    _dev2params = {
        DEVICES.CAX_DVF1 :
            # DVF1 Today: pixel size 4.8 um; magnification factor 0.5
            _get_namedtuple('DVFParameters',
            # _dvfparam_fields, (8, 0.5, 0.5, 0.005, 1024, 1280, 4.8, 0.5)),
            _dvfparam_fields, (8, 0.5, 0.5, 0.005, 2064, 3088, 2.4, 5.0)),
        DEVICES.CAX_DVF2 :
            # DVF2 today: pixel size 4.8 um; magnification factor 5.0
            # DVF2 future hifi: pixel size 2.4 um; magnification factor 5.0
            _get_namedtuple('DVFParameters',
            # _dvfparam_fields, (8, 0.5, 0.5, 0.005, 1024, 1280, 4.8, 5.0)),
            _dvfparam_fields, (8, 0.5, 0.5, 0.005, 2064, 3088, 2.4, 5.0)),
        }

    _properties = (
        'cam1:ArrayCallbacks', 'cam1:ArrayCallbacks_RBV',
        'cam1:AcquireTime', 'cam1:AcquireTime_RBV',
        'cam1:AcquirePeriod', 'cam1:AcquirePeriod_RBV',
        'cam1:Acquire', 'cam1:Acquire_RBV',
        'cam1:ImageMode', 'cam1:ImageMode_RBV',
        'cam1:Gain', 'cam1:Gain_RBV',
        'cam1:GainAuto', 'cam1:GainAuto_RBV',
        'cam1:PixelFormat', 'cam1:PixelFormat_RBV',
        'cam1:PixelSize', 'cam1:PixelSize_RBV',
        'cam1:SizeX_RBV', 'cam1:SizeY_RBV',
        'cam1:Temperature',
        'image1:EnableCallbacks', 'image1:EnableCallbacks_RBV',
        'image1:ArraySize0_RBV', 'image1:ArraySize1_RBV',
        'image1:ArrayData',
        'ffmstream1:EnableCallbacks', 'ffmstream1:EnableCallbacks_RBV',
        'Trans1:EnableCallbacks', 'Trans1:EnableCallbacks_RBV',
        'HDF1:EnableCallbacks', 'HDF1:EnableCallbacks_RBV',
        # 'Over1:EnableCallbacks', 'Over1:EnableCallbacks_RBV',
        # 'CC1:EnableCallbacks', 'CC1:EnableCallbacks_RBV',
        # 'CC1:ColorModeOut', 'CC1:ColorModeOut_RBV',
        # 'CC1:FalseColor', 'CC1:FalseColor_RBV',
        # 'DimFei1:EnableCallbacks', 'DimFei1:EnableCallbacks_RBV',
        )

    def __init__(self, devname, *args, **kwargs):
        """Init."""
        # check if device exists
        if devname not in DVF.DEVICES.ALL:
            raise NotImplementedError(devname)
        # call base class constructor
        super().__init__(devname, properties=self._properties, *args, **kwargs)

    @property
    def parameters(self):
        """Return DVF parameters."""
        return DVF._dev2params[self.devname]

    @property
    def intensity_saturation_value(self):
        """Image intensity saturation value."""
        # NOTE: a PV will be added to the IOC to select nr bits of intensity
        intensity_nr_bits = self.parameters.MAX_INTENSITY_NR_BITS
        return 2**intensity_nr_bits - 1

    @property
    def exposure_time(self):
        """Camera exposure time [s]."""
        return self['cam1:AcquireTime']

    @exposure_time.setter
    def exposure_time(self, value):
        """Camera exposure time [s]."""
        value = max(value, 0)
        self['cam1:AcquireTime'] = value

    @property
    def acquisition_time(self):
        """Camera acquisition time [s]."""
        return self['cam1:AcquirePeriod']

    @acquisition_time.setter
    def acquisition_time(self, value):
        """Camera acquisition time [s]."""
        params = self.parameters
        value = max(value, params.ACQUISITION_TIME_MIN)
        self['cam1:AcquirePeriod'] = value

    @property
    def acquisition_status(self):
        """Return IOC acquisition status."""
        return self['cam1:Acquire']

    @property
    def cam_sizex(self):
        """Camera second dimension size (pixels)."""
        return self['cam1:SizeX_RBV']

    @property
    def cam_sizey(self):
        """Camera first dimension size (pixels)."""
        return self['cam1:SizeY_RBV']

    @property
    def image_sizex(self):
        """Image second dimension size (pixels)."""
        return self['image1:ArraySize0_RBV']

    @property
    def image_sizey(self):
        """Image first dimension size (pixels)."""
        return self['image1:ArraySize1_RBV']

    @property
    def image(self):
        """Return DVF image formatted as a (sizey, sizex) numpy matrix."""
        shape = (self.image_sizey, self.image_sizex)
        data = self['image1:ArrayData']
        image = _np.reshape(data, shape)
        return image

    @property
    def image_pixel_size(self):
        """Image pixel size [um]."""
        params = self.parameters
        return params.IMAGE_PIXEL_SIZE

    @property
    def optics_magnification_factor(self):
        """Source to image magnification factor."""
        params = self.parameters
        return params.OPTICS_MAGNIFICATION_FACTOR

    @property
    def conv_pixel_2_srcsize(self):
        """Pixel to source size convertion factor."""
        pixel_size = self.image_pixel_size
        mag_factor = self.optics_magnefication_factor
        pixel2srcsize = pixel_size / mag_factor
        return pixel2srcsize

    @property
    def gain(self):
        """Return camera gain."""
        return self['cam1:Gain_RBV']

    @gain.setter
    def gain(self, value):
        """Set camera gain."""
        self['cam1:Gain'] = value

    @property
    def gain_auto(self):
        """Return camera gain auto."""
        return self['cam1:GainAuto_RBV']

    @gain.setter
    def gain_auto(self, value):
        """Set camera gain auto."""
        self['cam1:GainAuto'] = value

    @property
    def pixel_format(self):
        """Return camera pixel format."""
        return self['cam1:PixelFormat_RBV']

    @pixel_format.setter
    def pixel_format(self, value):
        """Set camera pixel format."""
        self['cam1:PixelFormat'] = value

    @property
    def pixel_size(self):
        """Return camera pixel size."""
        return self['cam1:PixelSize_RBV']

    @pixel_size.setter
    def pixel_size(self, value):
        """Set camera pixel size."""
        self['cam1:PixelSize'] = value

    @property
    def cam_temperature(self):
        """Return camera temperature"""
        return self['cam1:Temperature']

    def cmd_reset(self, timeout=None):
        """Reset DVF to a standard configuration."""
        props_values = {
            'cam1:ArrayCallbacks': 1,  # Enable
            'cam1:ImageMode': 2,  # Continuous
            'image1:EnableCallbacks': 1,  # Enable
            'ffmstream1:EnableCallbacks': 1,  # Enable
            'HDF1:EnableCallbacks': 1,  # Enable
            'Trans1:EnableCallbacks': 0,  # Disable
            # 'Over1:EnableCallbacks': 0,  # Disable
            # 'CC1:EnableCallbacks': 0,  # Disable
            # 'CC1:ColorModeOut': 0,  # Mono
            # 'CC1:FalseColor': 0,  # None
            # 'DimFei1:EnableCallbacks': 0,  # Disable
        }

        # set properties
        for propty, value in props_values.items():
            self[propty] = value

        # check readback values
        for propty, value in props_values.items():
            if not self._wait(propty + '_RBV', value, timeout=timeout):
                return False

        # configure image acquisition parameters
        params = self.parameters
        self.exposure_time = params.EXPOSURE_TIME_DEFAULT
        self.acquisition_time = params.ACQUISITION_TIME_DEFAULT
        return True

    def cmd_acquire_on(self, timeout=None):
        """Tune IOC image acquisition on."""
        return self._set_and_wait('cam1:Acquire', 1, timeout=timeout)

    def cmd_acquire_off(self, timeout=None):
        """Tune IOC image acquisition off."""
        return self._set_and_wait('cam1:Acquire', 0, timeout=timeout)

    def _set_and_wait(self, propty, value, timeout=None):
        """."""
        timeout = timeout or self._default_timeout
        self[propty] = value
        return self._wait(propty + '_RBV', value, timeout=timeout)


class DVFImgProc(DVF):
    """."""

    _properties = DVF._properties + (
        'ImgIntensityMax-Mon', 'ImgIntensityMin-Mon',
        'ImgIntensitySum-Mon', 'ImgIsSaturated-Mon',
        'ImgIsWithBeam-Mon',
        'ImgIsWithBeamThreshold-SP', 'ImgIsWithBeamThreshold-RB',

        'ImgROIX-RB', 'ImgROIX-SP',
        'ImgROIXCenter-Mon', 'ImgROIXFWHM-Mon',
        'ImgROIY-RB', 'ImgROIY-SP',
        'ImgROIYCenter-Mon', 'ImgROIYFWHM-Mon',

        'ImgLog-Mon',
        'ImgROIUpdateWithFWHM-Sel', 'ImgROIUpdateWithFWHM-Sts',
        'ImgROIYUpdateWithFWHMFactor-RB', 'ImgROIYUpdateWithFWHMFactor-SP',
        'ImgROIXUpdateWithFWHMFactor-RB', 'ImgROIXUpdateWithFWHMFactor-SP',

        'ImgROIXFitMean-Mon', 'ImgROIXFitSigma-Mon',
        'ImgROIXFitAmplitude-Mon', 'ImgROIXFitError-Mon',
        'ImgROIYFitMean-Mon', 'ImgROIYFitSigma-Mon',
        'ImgROIYFitAmplitude-Mon', 'ImgROIYFitError-Mon',
        'ImgFitAngle-Mon',
        'ImgFitSigma1-Mon', 'ImgFitSigma2-Mon',
        'ImgFitProcTime-Mon',
        'ImgFitAngleUseCMomSVD-Sel', 'ImgFitAngleUseCMomSVD-Sts',
        'ImgDVFStatus-Mon', 'ImgDVFStatusLabels-Cte',
        )

    def __init__(self, devname, *args, **kwargs):
        """."""
        super().__init__(devname=devname, *args, **kwargs)
        self._fitgaussian = _FitGaussianScipy()

    @property
    def intensity_min(self):
        """Image min intensity."""
        return self['ImgIntensityMin-Mon']

    @property
    def intensity_max(self):
        """Image max intensity."""
        return self['ImgIntensityMax-Mon']

    @property
    def intensity_sum(self):
        """Image sum intensity."""
        return self['ImgIntensitySum-Mon']

    @property
    def is_saturated(self):
        """Whether image is saturated."""
        return self['ImgIsSaturated-Mon']

    @property
    def is_with_beam(self):
        """Whether image is with beam."""
        return self['ImgIsWithBeam-Mon']

    @property
    def is_with_beam_threashold(self):
        """Get image is with beam threashold."""
        return self['ImgIsWithBeamThreshold-RB']

    @is_with_beam_threashold.setter
    def is_with_beam_threashold(self, value):
        """Set image is with beam threashold."""
        self['ImgIsWithBeamThreshold-SP'] = value

    @property
    def roiy(self):
        """."""
        return self['ImgROIY-RB']

    @roiy.setter
    def roiy(self, value):
        """."""
        self['ImgROIY-SP'] = value

    @property
    def roix(self):
        """."""
        return self['ImgROIX-RB']

    @roix.setter
    def roix(self, value):
        """."""
        self['ImgROIX-SP'] = value

    @property
    def roiy_center(self):
        """."""
        return self['ImgROIYCenter-Mon']

    @property
    def roix_center(self):
        """."""
        return self['ImgROIXCenter-Mon']

    @property
    def roiy_fwhm(self):
        """."""
        return self['ImgROIYFWHM-Mon']

    @property
    def roix_fwhm(self):
        """."""
        return self['ImgROIXFWHM-Mon']

    @property
    def roiy_fit_amplitude(self):
        """."""
        return self['ImgROIYFitAmplitude-Mon']

    @property
    def roix_fit_amplitude(self):
        """."""
        return self['ImgROIXFitAmplitude-Mon']

    @property
    def roiy_fit_mean(self):
        """."""
        return self['ImgROIYFitMean-Mon']

    @property
    def roix_fit_mean(self):
        """."""
        return self['ImgROIXFitMean-Mon']

    @property
    def roiy_fit_sigma(self):
        """."""
        return self['ImgROIYFitSigma-Mon']

    @property
    def roix_fit_sigma(self):
        """."""
        return self['ImgROIXFitSigma-Mon']

    @property
    def roiy_fit_error(self):
        """."""
        return self['ImgROIYFitError-Mon']

    @property
    def roix_fit_error(self):
        """."""
        return self['ImgROIXFitError-Mon']

    @property
    def roiy_fwhm_factor(self):
        """."""
        return self['ImgROIYUpdateWithFWHMFactor-RB']

    @roiy_fwhm_factor.setter
    def roiy_fwhm_factor(self, value):
        """."""
        self['ImgROIYUpdateWithFWHMFactor-SP'] = value

    @property
    def roix_fwhm_factor(self):
        """."""
        return self['ImgROIXUpdateWithFWHMFactor-RB']

    @roix_fwhm_factor.setter
    def roix_fwhm_factor(self, value):
        """."""
        self['ImgROIXUpdateWithFWHMFactor-SP'] = value

    @property
    def roi_update_with_fwhm(self):
        """."""
        return self['ImgROIUpdateWithFWHM-Sts']

    @roi_update_with_fwhm.setter
    def roi_update_with_fwhm(self, value):
        """."""
        self['ImgROIUpdateWithFWHM-Sel'] = bool(value)

    @property
    def fit_angle(self):
        """."""
        return self['ImgFitAngle-Mon']

    @property
    def fit_sigma1(self):
        """."""
        return self['ImgFitSigma1-Mon']

    @property
    def fit_sigma2(self):
        """."""
        return self['ImgFitSigma2-Mon']

    @property
    def fit_proctime(self):
        """Return image processing time [ms]."""
        return self['ImgFitProcTime-Mon']

    @property
    def fit_angle_use_cmom_svd(self):
        """."""
        return self['ImgFitAngleUseCMomSVD-Sts']

    @fit_angle_use_cmom_svd.setter
    def fit_angle_use_cmom_svd(self, value):
        """."""
        self['ImgFitAngleUseCMomSVD-Sel'] = bool(value)

    @property
    def log(self):
        """."""
        return self['ImgLog-Mon']

    def create_image2dfit(self):
        """Return a Image2DFit object with current image as data."""
        imgfit2d = _Image2D_Fit(
            data=self.image, fitgaussian=self._fitgaussian,
            roix=self.roix, roiy=self.roiy)
        return imgfit2d
