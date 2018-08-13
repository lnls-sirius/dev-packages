"""Main Module of the program."""

import time as _time
import numpy as _np
from threading import Thread
import logging as _log
from pcaspy import Driver as _PCasDriver
import siriuspy.csdevice.orbitcorr as _csorb
from si_ap_sofb.matrix import (
                            BaseMatrix as _BaseMatrix,
                            EpicsMatrix as _EpicsMatrix)
from si_ap_sofb.orbit import (
                            BaseOrbit as _BaseOrbit,
                            EpicsOrbit as _EpicsOrbit)
from si_ap_sofb.correctors import (
                            BaseCorrectors as _BaseCorrectors,
                            EpicsCorrectors as _EpicsCorrectors)
from si_ap_sofb.definitions import NR_BPMS, NR_CH, NR_CORRS, DANG, DFREQ


class SOFB:
    """Main Class of the IOC."""

    def get_database(self):
        """Get the database of the class."""
        db = _csorb.get_sofb_database(self.acc)
        prop = 'fun_set_pv'
        db['AutoCorr-Sel'][prop] = self.set_auto_corr
        db['AutoCorrFreq-SP'][prop] = self.set_auto_corr_frequency
        db['StartMeasRespMat-Cmd'][prop] = self.set_respmat_meas_state
        db['CorrMode-Sel'][prop] = self.set_correction_mode
        db['CalcCorr-Cmd'][prop] = self.calc_correction
        db['CorrFactorCH-SP'][prop] = lambda x: self.set_corr_factor('ch', x)
        db['CorrFactorCV-SP'][prop] = lambda x: self.set_corr_factor('cv', x)
        db['CorrFactorRF-SP'][prop] = lambda x: self.set_corr_factor('rf', x)
        db['MaxKickCH-SP'][prop] = lambda x: self.set_max_kick('ch', x)
        db['MaxKickCV-SP'][prop] = lambda x: self.set_max_kick('cv', x)
        db['MaxKickRF-SP'][prop] = lambda x: self.set_max_kick('rf', x)
        db['ApplyCorr-Cmd'][prop] = self.apply_corr
        db = {self.prefix + k: v for k, v in db.items()}
        db.update(self.correctors.get_database())
        db.update(self.matrix.get_database())
        db.update(self.orbit.get_database())
        return db

    def __init__(self, driver=None, orbit=None, matrix=None, correctors=None):
        """Initialize Object."""
        _log.info('Starting App...')
        self._driver = None
        self._orbit = self._correctors = self._matrix = None
        self._auto_corr = _csorb.AutoCorr.Off
        self._measuring_respmat = False
        self._auto_corr_freq = 1
        self._correction_mode = 1
        self._corr_factor = {'ch': 0.0, 'cv': 0.0, 'rf': 0.0}
        self._max_kick = {'ch': 300, 'cv': 300, 'rf': 3000}
        self._dtheta = None
        self._ref_corr_kicks = None
        self._thread = None
        self._database = self.get_database()

        self.driver = driver
        self.prefix = ''
        self.orbit = orbit
        self.correctors = correctors
        self.matrix = matrix
        if self.orbit is not None:
            self.orbit = _EpicsOrbit(
                            prefix=self.prefix, callback=self._update_driver)
        self.correctors = _EpicsCorrectors(
                            prefix=self.prefix, callback=self._update_driver)
        self.matrix = _EpicsMatrix(
                            prefix=self.prefix, callback=self._update_driver)

    @property
    def orbit(self):
        return self._orbit

    @orbit.setter
    def orbit(self, orb):
        if isinstance(orb, _BaseOrbit):
            self._orbit = orb

    @property
    def correctors(self):
        return self._correctors

    @correctors.setter
    def correctors(self, corrs):
        if isinstance(corrs, _BaseCorrectors):
            self._correctors = corrs

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, mat):
        if isinstance(mat, _BaseMatrix):
            self._matrix = mat

    @property
    def driver(self):
        """Set the driver of the instance."""
        return self._driver

    @driver.setter
    def driver(self, driver):
        if isinstance(driver, _PCasDriver):
            self._driver = driver

    def write(self, reason, value):
        """Write value in database."""
        _log.debug('App: Writing PV {0:s} with value {1:s}'.format(reason,
                                                                   str(value)))
        if not self._isValid(reason, value):
            return False
        fun_ = self._database[reason].get('fun_set_pv')
        if fun_ is None:
            _log.warning('App: Write unsuccessful. PV ' +
                         '{0:s} does not have a set function.'.format(reason))
            return False
        ret_val = fun_(value)
        if ret_val:
            _log.debug('App: Write complete.')
        else:
            _log.warning('App: Unsuccessful write of PV ' +
                         '{0:s}; value = {1:s}.'.format(reason, str(value)))
        return ret_val

    def process(self, interval):
        """Run continuously in the main thread."""
        t0 = _time.time()
        # _log.debug('App: Executing check.')
        # self.check()
        tf = _time.time()
        dt = (tf-t0)
        if dt > 0.2:
            _log.debug('App: check took {0:f}ms.'.format(dt*1000))
        dt = interval - dt
        if dt > 0:
            _time.sleep(dt)

    def apply_corr(self, code):
        """Apply calculated kicks on the correctors."""
        if not self._correction_mode:
            self._call_callback('Log-Mon', 'Err: Offline, cannot apply kicks.')
            return False
        if self._thread and self._thread.is_alive():
            self._call_callback('Log-Mon',
                                'Err: AutoCorr or MeasRespMat is On.')
            return False
        if self._dtheta is None:
            self._call_callback('Log-Mon',
                                'Err: Cannot Apply Kick. Calc Corr first.')
            return False
        Thread(target=self._apply_corr,
               kwargs={'code': code},
               daemon=True).start()
        return True

    def calc_correction(self, value):
        """Calculate correction."""
        if self._thread and self._thread.is_alive():
            self._call_callback('Log-Mon',
                                'Err: AutoCorr or MeasRespMat is On.')
            return False
        Thread(target=self._calc_correction, daemon=True).start()
        return True

    def set_respmat_meas_state(self, value):
        if value == _csorb.MeasRespMatCmd.Start:
            self._start_meas_respmat()
        elif value == _csorb.MeasRespMatCmd.Stop:
            self._stop_meas_respmat()
        elif value == _csorb.MeasRespMatCmd.Reset:
            self._reset_meas_respmat()

    def set_auto_corr(self, value):
        if value == _csorb.AutoCorr.On:
            if self._auto_corr == _csorb.AutoCorr.On:
                self._call_callback('Log-Mon', 'Err: AutoCorr is Already On.')
                return False
            self._auto_corr = value
            if self._thread and self._thread.is_alive():
                self._call_callback('Log-Mon',
                                    'Err: Cannot Correct, Measuring RespMat.')
                return False
            self._call_callback('Log-Mon', 'Turning Auto Correction On.')
            self._thread = Thread(target=self._do_auto_corr,
                                  daemon=True)
            self._thread.start()
        elif value == _csorb.AutoCorr.Off:
            self._call_callback('Log-Mon', 'Turning Auto Correction Off.')
            self._auto_corr = value
        return True

    def set_correction_mode(self, value):
        self._correction_mode = value
        self.orbit.correction_mode = value
        self._call_callback(
            'Log-Mon',
            'Changing to {0:s} mode.'.format(_csorb.CorrMode._fields[value])
            )
        self._call_callback('CorrMode-Sts', value)
        self.orbit.get_orbit()
        return True

    def set_auto_corr_frequency(self, value):
        self._auto_corr_freq = value
        self._call_callback('AutoCorrFreq-RB', value)
        return True

    def set_max_kick(self, plane, value):
        self._max_kick[plane] = float(value)
        self._call_callback('MaxKick'+plane.upper()+'-RB', float(value))

    def set_corr_factor(self, plane, value):
        self._corr_factor[plane] = value/100
        self._call_callback(
            'Log-Mon',
            '{0:s} CorrFactor set to {1:6.2f}'.format(plane.upper(), value))
        self._call_callback('CorrFactor'+plane.upper()+'-RB', value)
        return True

    def _apply_corr(self, code):
        kicks = self._dtheta.copy()
        if code == _csorb.ApplyCorr.CH:
            kicks[NR_CH:] = 0
        elif code == _csorb.ApplyCorr.CV:
            kicks[:NR_CH] = 0
            kicks[-1] = 0
        elif code == _csorb.ApplyCorr.RF:
            kicks[:-1] = 0
        self._call_callback(
            'Log-Mon',
            'Applying {0:s} kicks.'.format(_csorb.ApplyCorr._fields[code]))
        kicks = self._process_kicks(kicks)
        if any(kicks):
            self.correctors.apply_kicks(self._ref_corr_kicks + kicks)

    def _call_callback(self, pv, value):
        self._update_driver(self.prefix + pv, value)

    def _update_driver(self, pvname, value, **kwargs):
        _log.debug('PV {0:s} updated in driver '.format(pvname) +
                   'database with value {0:s}'.format(str(value)))
        self._driver.setParam(pvname, value)
        self._driver.updatePVs()

    def _isValid(self, reason, value):
        if reason.endswith(('-Sts', '-RB', '-Mon')):
            _log.debug('App: PV {0:s} is read only.'.format(reason))
            return False
        enums = self._database[reason].get('enums')
        if enums is not None:
            if isinstance(value, int):
                if value >= len(enums):
                    _log.warning('App: value {0:d} too large '.format(value) +
                                 'for PV {0:s} of type enum'.format(reason))
                    return False
            elif isinstance(value, str):
                if value not in enums:
                    _log.warning('Value {0:s} not permited'.format(value))
                    return False
        return True

    def _stop_meas_respmat(self):
        if not self._measuring_respmat:
            self._call_callback('Log-Mon', 'Err :No Measurement ocurring.')
            return False
        self._call_callback('Log-Mon', 'Aborting measurement.')
        self._measuring_respmat = False
        self._thread.join()
        self._call_callback('Log-Mon', 'Measurement aborted.')
        return True

    def _reset_meas_respmat(self):
        if self._measuring_respmat:
            self._call_callback('Log-Mon',
                                'Cannot Reset, Measurement in process.')
            return False
        self._call_callback('Log-Mon', 'Reseting measurement status.')
        self._call_callback('MeasRespMat-Mon', _csorb.MeasRespMatMon.Idle)
        return True

    def _start_meas_respmat(self):
        if self._measuring_respmat:
            self._call_callback('Log-Mon',
                                'Err: Measurement already in process.')
            return False
        if self._thread and self._thread.is_alive():
            self._call_callback('Log-Mon',
                                'Err: Cannot Measure, AutoCorr is On.')
            return False
        self._measuring_respmat = True
        self._call_callback('Log-Mon', 'Starting RSP Matrix measurement.')
        self._thread = Thread(target=self._do_meas_respmat, daemon=True)
        self._thread.start()
        return True

    def _do_meas_respmat(self):
        self._call_callback('MeasRespMat-Mon', _csorb.MeasRespMatMon.Measuring)
        mat = _np.zeros([2*NR_BPMS, NR_CORRS])
        orig_kicks = self.correctors.get_strength()
        for i in range(NR_CORRS):
            if not self._measuring_respmat:
                self._call_callback(
                            'MeasRespMat-Mon', _csorb.MeasRespMatMon.Aborted)
                self.correctors.apply_kicks(orig_kicks)
                return
            self._call_callback(
                'Log-Mon',
                'Varying Corrector {0:d} of {1:d}'.format(i, NR_CORRS)
                )
            delta = DANG if i < NR_CORRS-1 else DFREQ
            kicks = orig_kicks.copy()
            kicks[i] += delta/2
            self.correctors.apply_kicks(kicks)
            orbp = self.orbit.get_orbit(True)
            kicks[i] += -delta
            self.correctors.apply_kicks(kicks)
            orbn = self.orbit.get_orbit(True)
            mat[:, i] = (orbp-orbn)/delta
        self.correctors.apply_kicks(orig_kicks)
        self._call_callback('Log-Mon', 'Measurement Completed.')
        self.set_respmat(list(mat.flatten()))
        self._call_callback('MeasRespMat-Mon', _csorb.MeasRespMatMon.Completed)
        self._measuring_respmat = False

    def _do_auto_corr(self):
        if not self._correction_mode:
            self._call_callback('Log-Mon',
                                'Err: Cannot Auto Correct in Offline Mode')
            self._call_callback('AutoCorr-Sel', 0)
            self._call_callback('AutoCorr-Sts', 0)
            return
        self._call_callback('AutoCorr-Sts', 1)
        while self._auto_corr == _csorb.AutoCorr.On:
            t0 = _time.time()
            orb = self.orbit.get_orbit()
            kicks = self.matrix.calc_kicks(orb)
            kicks = self._process_kicks(kicks)
            kicks += self.correctors.get_strength()
            self.correctors.apply_kicks(kicks)
            tf = _time.time()
            dt = (tf-t0)
            interval = 1/self._auto_corr_freq
            if dt > interval:
                _log.debug('App: check took {0:f}ms.'.format(dt*1000))
                self._call_callback(
                    'Log-Mon',
                    'Warn: Auto Corr Loop took {0:6.2f}ms.'.format(dt*1000)
                    )
            dt = interval - dt
            if dt > 0:
                _time.sleep(dt)
        self._call_callback('Log-Mon', 'Auto Correction is Off.')
        self._call_callback('AutoCorr-Sts', 0)

    def _calc_correction(self):
        self._call_callback('Log-Mon', 'Getting the orbit.')
        orb = self.orbit.get_orbit()
        self._call_callback('Log-Mon', 'Calculating the kicks.')
        self._ref_corr_kicks = self.correctors.get_strength()
        self._dtheta = self.matrix.calc_kicks(orb)

    def _process_kicks(self, kicks):
        kicks[:NR_CH] *= self._corr_factor['ch']
        kicks[NR_CH:-1] *= self._corr_factor['cv']
        kicks[-1] *= self._corr_factor['rf']

        max_kick_ch = max(abs(kicks[:NR_CH]))
        if max_kick_ch > self._max_kick['ch']:
            factor = self._max_kick['ch']/max_kick_ch
            kicks[:NR_CH] *= factor
            percent = self._corr_factor['ch'] * factor * 100
            self._call_callback(
                'Log-Mon',
                'Warn: CH kick > MaxKickCH. Using {0:5.2f}%'.format(percent)
                )
        max_kick_cv = max(abs(kicks[NR_CH:-1]))
        if max_kick_cv > self._max_kick['cv']:
            factor = self._max_kick['cv']/max_kick_cv
            kicks[NR_CH:-1] *= factor
            percent = self._corr_factor['cv'] * factor * 100
            self._call_callback(
                'Log-Mon',
                'Warn: CV kick > MaxKickCV. Using {0:5.2f}%'.format(percent)
                )
        if abs(kicks[-1]) > self._max_kick['rf']:
            factor = self._max_kick['rf'] / abs(kicks[-1])
            kicks[-1] *= factor
            percent = self._corr_factor['rf'] * factor * 100
            self._call_callback(
                'Log-Mon',
                'Warn: RF kick > MaxKickRF. Using {0:5.2f}%'.format(percent)
                )
        return kicks
