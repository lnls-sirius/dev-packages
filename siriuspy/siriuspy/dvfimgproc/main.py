"""Module with main IOC Class."""

import time as _time
import logging as _log
import numpy as _np

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

from ..logging import get_logger as _get_logger

from .meas import MeasDVF


class App:
    """BL Image Processing IOC Application."""

    CHECK_IMG_ACQUIRE = True

    _MON_PVS_2_IMGFIT = {
        # These PVs are updated at evry image processing
        # --- image intensity ---
        'ImgSizeX-Mon': ('fitx', 'size'),
        'ImgSizeY-Mon': ('fity', 'size'),
        'ImgIntensityMin-Mon': 'intensity_min',
        'ImgIntensityMax-Mon': 'intensity_max',
        'ImgIntensitySum-Mon': 'intensity_sum',
        'ImgIsSaturated-Mon': 'is_saturated',
        # --- image projection ---
        'ImgProjX-Mon': ('fitx', 'data'),
        'ImgProjY-Mon': ('fity', 'data'),
        'ImgIsWithBeam-Mon': 'is_with_image',
        # --- roix ---
        'ImgROIX-RB': ('fitx', 'roi'),
        'ImgROIXCenter-Mon': ('fitx', 'roi_center'),
        'ImgROIXFWHM-Mon': ('fitx', 'roi_fwhm'),
        # --- roix_fit ---
        'ImgROIXFitAmplitude-Mon': ('fitx', 'roi_amplitude'),
        'ImgROIXFitMean-Mon': ('fitx', 'roi_mean'),
        'ImgROIXFitSigma-Mon': ('fitx', 'roi_sigma'),
        'ImgROIXFitError-Mon': ('fitx', 'roi_fit_error'),
        # --- roixy ---
        'ImgROIY-RB': ('fity', 'roi'),
        'ImgROIYCenter-Mon': ('fity', 'roi_center'),
        'ImgROIYFWHM-Mon': ('fity', 'roi_fwhm'),
        # --- roiy_fit ---
        'ImgROIYFitAmplitude-Mon': ('fity', 'roi_amplitude'),
        'ImgROIYFitMean-Mon': ('fity', 'roi_mean'),
        'ImgROIYFitSigma-Mon': ('fity', 'roi_sigma'),
        'ImgROIYFitError-Mon': ('fity', 'roi_fit_error'),
        # --- gauss2d fit ---
        'ImgFitAngle-Mon': 'angle',
        'ImgFitSigma1-Mon': 'sigma1',
        'ImgFitSigma2-Mon': 'sigma2',
    }

    _INIT_PVS_2_IMGFIT = {
        # These are either constant PVs or readback PVs whose
        # initializations need external input
        'ImgROIX-RB': ('fitx', 'roi'),
        'ImgROIY-RB': ('fity', 'roi'),
        'ImgROIX-SP': ('fitx', 'roi'),
        'ImgROIY-SP': ('fity', 'roi'),
    }

    def __init__(self, driver=None, const=None):
        """Initialize the instance."""
        self._driver = driver
        self._const = const
        self._database = const.get_database()
        self._heartbeat = 0
        self._timestamp_last_update = _time.time()
        self._init_driver_flag = False
        self._logger = _get_logger(self)

        # create measurement object
        self._meas = self._create_meas()

        # add epics app callback to measurement
        self._meas.callback = self.update_driver

    @property
    def const(self):
        """."""
        return self._const

    @property
    def driver(self):
        """."""
        return self._driver

    @driver.setter
    def driver(self, value):
        """."""
        self._driver = value

    @property
    def meas(self):
        """."""
        return self._meas

    @property
    def heartbeat(self):
        """."""
        return self._heartbeat

    def increment_heartbeat(self):
        """."""
        self._heartbeat += 1

    def process(self, interval):
        """Run continuously in the main thread."""
        # update heartbeat
        self.increment_heartbeat()
        self._write_pv('ImgTimestampUpdate-Mon', _time.time())

        # if enabled, check if image acquisition is not working and set it
        if App.CHECK_IMG_ACQUIRE:
            self._check_acquisition_timeout()

        _time.sleep(interval)

    def write(self, reason, value):
        """Write value in objects and database."""
        pv_is_writable = reason.endswith('-SP') \
            or reason.endswith('-Sel') \
            or reason.endswith('-Cmd')
        if not pv_is_writable:
            self._logger.warning(
                'PV %s is not writable!', reason, extra={'ioc_only': True}
            )
            return False

        res = self._write_roi(reason, value)
        if res is not None:
            return res

        res = self._write_fwhm_factor(reason, value)
        if res is not None:
            return res

        res = self._write_iswithbeam_threshold(reason, value)
        if res is not None:
            return res

        res = self._write_update_roi_with_fwhm(reason, value)
        if res is not None:
            return res

        res = self._write_use_svd4theta(reason, value)
        if res is not None:
            return res

        res = self._write_dvf_reset(reason, value)
        if res is not None:
            return res

        res = self._write_dvf_acquire(reason, value)
        if res is not None:
            return res

        return True

    def init_driver(self):
        """Initialize PVs at startup."""
        self._init_driver_flag = True
        self._write_pv('ImgDVFSizeX-Cte', self.meas.dvf_sizex)
        self._write_pv('ImgDVFSizeY-Cte', self.meas.dvf_sizey)

        msgfmt_nok = 'PV {} could not be initialized!'
        for pvname, attr in App._INIT_PVS_2_IMGFIT.items():
            if self.meas.status == self.meas.STATUS_SUCCESS:
                # update epics db successfully
                value = self._conv_imgattr2value(attr)
                if value is None:
                    self._logger.warning(
                        msgfmt_nok.format(pvname), extra={'ioc_only': True}
                    )
                    self._write_pv_failed(pvname)
                    self._init_driver_flag = False
                else:
                    self._logger.info(
                        'PV %s initialized.', pvname, extra={'ioc_only': True}
                    )
                    self._write_pv(pvname, value)
            else:
                self._logger.warning(
                    msgfmt_nok.format(pvname), extra={'ioc_only': True}
                )
                self._write_pv_failed(pvname)
                self._init_driver_flag = False

    def update_driver(self):
        """Update all parameters at every image PV callback."""
        self._timestamp_last_update = _time.time()

        if not self._init_driver_flag:
            self.init_driver()

        if not self.meas.image2dfit.is_with_image:
            self._write_pv('ImgIsWithBeam-Mon', 0)
            return

        invalid_fitx, invalid_fity = [False]*2
        for pvname, attr in App._MON_PVS_2_IMGFIT.items():
            # check if is roi_rb and if it needs updating
            if pvname in ('ImgROIX-RB', 'ImgROIY-RB'):
                if not self.meas.update_roi_with_fwhm:
                    continue

            # get image attribute value
            value = self._conv_imgattr2value(attr)
            if value is None:
                self._logger.warning(
                    'PV %s could not be updated with None value!',
                    pvname,
                    extra={'ioc_only': True}
                )
                continue

            # check if fit is valid and update value
            invalid_fit, new_value = self._check_invalid_fit(pvname, value)
            invalid_fitx |= invalid_fit if 'XFit' in pvname else False
            invalid_fity |= invalid_fit if 'YFit' in pvname else False

            # update epics db
            if self.meas.status == self.meas.STATUS_SUCCESS:
                self._write_pv(pvname, new_value)
            else:
                self._write_pv_failed(pvname)

        if invalid_fitx:
            self._logger.warning('Invalid ROIXFit')
        if invalid_fity:
            self._logger.warning('Invalid ROIYFit')

        if self.meas.status != self.meas.STATUS_SUCCESS:
            self._logger.warning(self.meas.status)
        else:
            if self.meas.proc_time is not None:
                self._write_pv('ImgFitProcTime-Mon', self.meas.proc_time)
            self._write_pv('ImgDVFStatus-Mon', self.meas.status_dvf)

    def update_log(self, message):
        """."""
        message = message + f'[{self.heartbeat}] '
        self._write_pv('ImgLog-Mon', message)

    def _check_acquisition_timeout(self):
        """."""
        interval = _time.time() - self._timestamp_last_update
        if self.meas.acquisition_timeout(interval):
            self._logger.warning('DVF Image update timeout!')
            self._timestamp_last_update = _time.time()

    def _check_invalid_fit(self, pvname, value):
        """."""
        if 'XFit' in pvname:
            invalid_fit = self.meas.image2dfit.fitx.invalid_fit
        elif 'YFit' in pvname:
            invalid_fit = self.meas.image2dfit.fity.invalid_fit
        elif 'FitAngle' in pvname:
            invalid_fit = \
                self.meas.image2dfit.fitx.invalid_fit or \
                self.meas.image2dfit.fity.invalid_fit
        else:
            invalid_fit = False

        if invalid_fit:
            new_value = 0
        else:
            new_value = value
        return invalid_fit, new_value

    def _create_meas(self):
        # build arguments
        fwhmx_factor = \
            float(self._database['ImgROIXUpdateWithFWHMFactor-RB']['value'])
        fwhmy_factor = \
            float(self._database['ImgROIYUpdateWithFWHMFactor-RB']['value'])
        roi_with_fwhm = \
            float(self._database['ImgROIUpdateWithFWHM-Sts']['value'])
        intensity_threshold = \
            int(self._database['ImgIsWithBeamThreshold-RB']['value'])
        use_svd4theta = \
            int(self._database['ImgFitAngleUseCMomSVD-Sts']['value'])

        # create object
        meas = MeasDVF(
            self.const.devname,
            fwhmx_factor=fwhmx_factor, fwhmy_factor=fwhmy_factor,
            roi_with_fwhm=roi_with_fwhm,
            intensity_threshold=intensity_threshold,
            use_svd4theta=use_svd4theta,
        )
        return meas

    def _write_pv(self, pvname, value=None, success=True):
        """."""
        if success:
            if isinstance(value, (bool, _np.bool_)):
                value = 1 if value else 0
            try:
                self._driver.setParam(pvname, value)
                self._driver.updatePV(pvname)
            except TypeError:
                self._logger.warning(
                    '_write_pv: error in updatePV for %s %d',
                    pvname,
                    value,
                    extra={'ioc_only': True}
                )
            self._driver.setParamStatus(
                pvname, _Alarm.NO_ALARM, _Severity.NO_ALARM)
        else:
            self._logger.debug(
                '%s: updated with alarm', pvname, extra={'ioc_only': True}
            )
            self._driver.setParamStatus(
                pvname, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)

    def _write_pv_failed(self, pvname):
        # update epics db failure
        self._write_pv(pvname, success=False)
        # update Log
        self._logger.warning(self.meas.status)

    def _write_pv_sp_rb(self, reason, value):
        # update SP/Sel
        self._write_pv(reason, value)

        # update RB/Sts
        reason = reason.replace('-SP', '-RB').replace('-Sel', '-Sts')
        self._write_pv(reason, value)

    def _write_roi(self, reason, value):
        if reason not in ('ImgROIX-SP', 'ImgROIY-SP'):
            return None
        if 'X' in reason:
            self.meas.set_roix(value)
        else:
            self._meas.set_roiy(value)

        if self.meas.status == self.meas.STATUS_SUCCESS:
            self._write_pv_sp_rb(reason, value)
            return True
        else:
            self._logger.warning(f'{reason}: could not write value {value}')
            return False

    def _write_use_svd4theta(self, reason, value):
        if reason != 'ImgFitAngleUseCMomSVD-Sel':
            return None

        self.meas.set_use_svd4theta(value)

        if self.meas.status == self.meas.STATUS_SUCCESS:
            self._write_pv_sp_rb(reason, value)
            return True
        else:
            self._logger.warning(f'{reason}: could not write value {value}')
            return False

    def _write_iswithbeam_threshold(self, reason, value):
        if reason != 'ImgIsWithBeamThreshold-SP':
            return None

        # set threshold
        self.meas.set_intensity_threshold(value)

        if self.meas.status == self.meas.STATUS_SUCCESS:
            self._write_pv_sp_rb(reason, value)
            return True
        else:
            self._logger.warning(f'{reason}: could not write value {value}')
            return False

    def _write_dvf_reset(self, reason, value):
        """."""
        if reason != 'ImgDVFReset-Cmd':
            return None

        # set acquire
        if self.meas.reset_dvf():
            value = self._driver.getParam(reason)
            self._driver.setParam(reason, value + 1)
            self._driver.updatePV(reason)
            return True
        else:
            self._logger.warning(f'{reason}: could not execute')
            return False

    def _write_dvf_acquire(self, reason, value):
        """."""
        if reason != 'ImgDVFAcquire-Cmd':
            return None

        # set acquire
        if self.meas.set_acquire():
            value = self._driver.getParam(reason)
            self._driver.setParam(reason, value + 1)
            self._driver.updatePV(reason)
            return True
        else:
            self._logger.warning(f'{reason}: could not execute')
            return False

    def _write_fwhm_factor(self, reason, value):
        if reason not in (
                'ImgROIXUpdateWithFWHMFactor-SP',
                'ImgROIYUpdateWithFWHMFactor-SP'):
            return None
        if 'X' in reason:
            self.meas.fwhmx_factor = value
        else:
            self.meas.fwhmy_factor = value
        self._write_pv_sp_rb(reason, value)
        return True

    def _write_update_roi_with_fwhm(self, reason, value):
        """."""
        if reason not in ('ImgROIUpdateWithFWHM-Sel'):
            return None
        self.meas.update_roi_with_fwhm = value
        self._write_pv_sp_rb(reason, value)
        return True

    def _conv_imgattr2value(self, attr):
        value = self.meas.image2dfit
        if value is None:
            # image2dfit object anomalously not created yet!
            return None
        if isinstance(attr, tuple):
            for obj in attr:
                value = getattr(value, obj)
        else:
            value = getattr(value, attr)
        return value
