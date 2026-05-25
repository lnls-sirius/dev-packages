"""."""

import time as _time
import logging as _log

from mathphys import imgproc as _imgproc

from ..epics import CAThread as _Thread
from ..devices import DVF as _DVF


class MeasDVF():
    """."""

    STATUS_SUCCESS = ''
    DVF_IMAGE_PROPTY = 'image1:ArrayData'
    MIN_ROI_SIZE = 5  # [pixels]

    def __init__(
            self, const, fwhmx_factor, fwhmy_factor, roi_with_fwhm,
            intensity_threshold, use_svd4theta, callback=None):
        """."""
        self._const = const
        self._devname = const.devname
        self._callback = callback
        self._status = MeasDVF.STATUS_SUCCESS
        self._dvf = None
        self._fitgauss = _imgproc.FitGaussianScipy()  # needs scipy
        self._image2dfit = None
        self._fwhmx_factor = fwhmx_factor
        self._fwhmy_factor = fwhmy_factor
        self._intensity_threshold = intensity_threshold
        self._use_svd4theta = use_svd4theta
        self._roi_with_fwhm = roi_with_fwhm
        self._proc_time = None

        # create DVF device
        self._create_dvf()

        # init image2dfit object
        self.process_image()

        # add callback
        self._thread = None
        self._imgpv = self._dvf.pv_object(MeasDVF.DVF_IMAGE_PROPTY)
        self._imgpv.add_callback(self._start_imgproc)
        self._imgpv.auto_monitor = True

    @property
    def devname(self):
        """."""
        return self._devname

    @property
    def dvf(self):
        """."""
        return self._dvf

    @property
    def status_dvf(self):
        """."""
        status = 0 * self._const.DEF_DVFSTATUS
        status |= ((1 if not self.dvf.connected else 0) << 0)
        status |= ((1 if not self.dvf.acquisition_status else 0) << 1)
        return status

    @property
    def image2dfit(self):
        """."""
        return self._image2dfit

    @property
    def dvf_sizex(self):
        """."""
        return self._dvf.parameters.IMAGE_SIZE_X

    @property
    def dvf_sizey(self):
        """."""
        return self._dvf.parameters.IMAGE_SIZE_Y

    @property
    def fwhmx_factor(self):
        """."""
        return self._fwhmx_factor

    @fwhmx_factor.setter
    def fwhmx_factor(self, value):
        """."""
        self._fwhmx_factor = value

    @property
    def fwhmy_factor(self):
        """."""
        return self._fwhmy_factor

    @fwhmy_factor.setter
    def fwhmy_factor(self, value):
        """."""
        self._fwhmy_factor = value

    @property
    def intensity_threshold(self):
        """."""
        return self._intensity_threshold

    @property
    def status(self):
        """."""
        return self._status

    @property
    def update_roi_with_fwhm(self):
        """."""
        return self._roi_with_fwhm

    @update_roi_with_fwhm.setter
    def update_roi_with_fwhm(self, value):
        """."""
        self._roi_with_fwhm = value

    @property
    def callback(self):
        """."""
        return self._callback

    @callback.setter
    def callback(self, value):
        """."""
        self._callback = value

    @property
    def proc_time(self):
        """."""
        return self._proc_time

    def acquisition_timeout(self, interval):
        """Check if given interval defines an image update timeout."""
        if self.dvf.acquisition_time:
            return interval > 10 * self.dvf.acquisition_time
        return False

    def reset_dvf(self):
        """Reset DVF."""
        if self.dvf.connected:
            return self._dvf.cmd_reset()
        else:
            return False

    def set_acquire(self):
        """."""
        if self.dvf.connected:
            if not self.dvf.cmd_acquire_off():
                return False
            if not self.dvf.cmd_acquire_on():
                return False
            return True
        return False

    def set_roix(self, value):
        """."""
        _, roiy = self._image2dfit.roi
        try:
            self._image2dfit.roi = [value, roiy]
            self._status = MeasDVF.STATUS_SUCCESS
        except Exception:
            self._status = 'Unable to set ROIX'

    def set_roiy(self, value):
        """."""
        roix, _ = self._image2dfit.roi
        try:
            self._image2dfit.roi = [roix, value]
            self._status = MeasDVF.STATUS_SUCCESS
        except Exception:
            self._status = 'Unable to set ROIY'

    def set_intensity_threshold(self, value):
        """."""
        try:
            self._image2dfit.intensity_threshold = int(value)
            self._status = MeasDVF.STATUS_SUCCESS
            self._intensity_threshold = self._image2dfit.intensity_threshold
        except Exception:
            self._status = 'Unable to set intensity threshold'

    def set_use_svd4theta(self, value):
        """."""
        try:
            self._image2dfit.use_svd4theta = value
            self._status = MeasDVF.STATUS_SUCCESS
            self._use_svd4theta = self._image2dfit.use_svd4theta
        except Exception:
            self._status = 'Unable to set angle fit method'

    def process_image(self, **kwargs):
        """Process image."""
        # assume image can be processed for the time being
        self._status = MeasDVF.STATUS_SUCCESS

        # check if DVF is connected
        if not self._dvf.connected:
            self._status = 'DVF not connected'
            return

        # symbol to image2d fit object
        img2dfit = self._image2dfit

        # define roi based on previus image or fwhm factors
        if not self._image2dfit:
            # no image2dfit yet
            roix, roiy = (None, None)
        elif self.update_roi_with_fwhm:
            # recalc roi using fwhm factors
            roix = img2dfit.fitx.calc_roi_with_fwhm(
                image=img2dfit.fitx, fwhm_factor=self.fwhmx_factor)
            roiy = img2dfit.fity.calc_roi_with_fwhm(
                image=img2dfit.fity, fwhm_factor=self.fwhmy_factor)
            if roix[1] - roix[0] < MeasDVF.MIN_ROI_SIZE:
                roix = None
            if roiy[1] - roiy[0] < MeasDVF.MIN_ROI_SIZE:
                roiy = None
        else:
            # reuse current roi for new image
            roix = self._image2dfit.fitx.roi
            roiy = self._image2dfit.fity.roi

        # get image data and process fitting
        try:
            t0_ = _time.time()
            data = self._dvf.image
            saturation_threshold = self._dvf.intensity_saturation_value
            use_svd4theta = self._use_svd4theta
            self._image2dfit = _imgproc.Image2D_Fit(
                data=data, fitgauss=self._fitgauss,
                saturation_threshold=saturation_threshold,
                intensity_threshold=self._intensity_threshold,
                roix=roix, roiy=roiy, use_svd4theta=use_svd4theta)
            self._proc_time = 1000 * (_time.time() - t0_)
        except Exception as err:
            message = str(err)
            _log.warning(message)
            self._status = \
                f'Unable to process image'

        # run registered driver callback
        if self._callback:
            self._callback()

    def _start_imgproc(self, *args, **kwargs):
        """."""
        if self._thread and self._thread.is_alive():
            return
        self._thread = _Thread(target=self.process_image, daemon=True)
        self._thread.start()

    def _create_dvf(self):
        """Create DVF object and add process_image callback."""
        self._dvf = _DVF(self._devname)
