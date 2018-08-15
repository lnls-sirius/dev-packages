"""Main Module of the program."""

import time as _time
import numpy as _np
import logging as _log
from functools import partial as _part
from threading import Thread as _Thread
from pcaspy import Driver as _PCasDriver
import siriuspy.csdevice.orbitcorr as _csorb
from siriuspy.thread import QueueThread as _Queue, RepeaterThread as _Repeat
from .matrix import BaseMatrix as _BaseMatrix, EpicsMatrix as _EpicsMatrix
from .orbit import BaseOrbit as _BaseOrbit, EpicsOrbit as _EpicsOrbit
from .correctors import (BaseCorrectors as _BaseCorrectors,
                         EpicsCorrectors as _EpicsCorrectors)
from .base_class import BaseClass as _BaseClass

INTERVAL = 0.1


class SOFB(_BaseClass):
    """Main Class of the IOC."""

    def get_database(self):
        """Get the database of the class."""
        db = _csorb.get_sofb_database(self.acc)
        prop = 'fun_set_pv'
        db['AutoCorr-Sel'][prop] = self.set_auto_corr
        db['AutoCorrFreq-SP'][prop] = self.set_auto_corr_frequency
        db['StartMeasRespMat-Cmd'][prop] = self.set_respmat_meas_state
        db['CalcCorr-Cmd'][prop] = self.calc_correction
        db['CorrFactorCH-SP'][prop] = _part(self.set_corr_factor, 'ch')
        db['CorrFactorCV-SP'][prop] = _part(self.set_corr_factor, 'cv')
        db['CorrFactorRF-SP'][prop] = _part(self.set_corr_factor, 'rf')
        db['MaxKickCH-SP'][prop] = _part(self.set_max_kick, 'ch')
        db['MaxKickCV-SP'][prop] = _part(self.set_max_kick, 'cv')
        db['MaxKickRF-SP'][prop] = _part(self.set_max_kick, 'rf')
        db['MeasRespMatKickCH-SP'][prop] = _part(self.set_respmat_kick, 'ch')
        db['MeasRespMatKickCV-SP'][prop] = _part(self.set_respmat_kick, 'cv')
        db['MeasRespMatKickRF-SP'][prop] = _part(self.set_respmat_kick, 'rf')
        db['ApplyCorr-Cmd'][prop] = self.apply_corr
        db = super().get_database(db)
        db.update(self.correctors.get_database())
        db.update(self.matrix.get_database())
        db.update(self.orbit.get_database())
        return db

    def __init__(self, acc, prefix='', callback=None,
                 orbit=None, matrix=None, correctors=None):
        """Initialize Object."""
        super().__init__(acc, prefix=prefix, callback=callback)
        _log.info('Starting SOFB...')
        self._driver = None
        self._orbit = self._correctors = self._matrix = None
        self._auto_corr = _csorb.AutoCorr.Off
        self._measuring_respmat = False
        self._auto_corr_freq = 1
        self._corr_factor = {'ch': 0.0, 'cv': 0.0, 'rf': 0.0}
        self._max_kick = {'ch': 300, 'cv': 300, 'rf': 3000}
        self._meas_respmat_kick = {'ch': 0.2, 'cv': 0.2, 'rf': 200}
        self._dtheta = None
        self._ref_corr_kicks = None
        self._thread = None
        self._database = self.get_database()
        self._queue = _Queue()
        self._queue.start()

        self.orbit = orbit
        self.correctors = correctors
        self.matrix = matrix
        if self._orbit is None:
            self.orbit = _EpicsOrbit(acc=acc, prefix=self.prefix)
        if self._correctors is None:
            self.correctors = _EpicsCorrectors(acc=acc, prefix=self.prefix)
        if self._matrix is None:
            self.matrix = _EpicsMatrix(acc=acc, prefix=self.prefix)
        self.add_callback(self._schedule_update)
        self._orbit.add_callback(self._schedule_update)
        self._correctors.add_callback(self._schedule_update)
        self._matrix.add_callback(self._schedule_update)

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
        if not self._isValid(reason, value):
            return False
        fun_ = self._database[reason].get('fun_set_pv')
        if fun_ is None:
            _log.warning('Write unsuccessful. PV ' +
                         '{0:s} does not have a set function.'.format(reason))
            return False
        ret_val = fun_(value)
        if ret_val:
            _log.debug('Write complete.')
        else:
            _log.warning('Unsuccessful write of PV ' +
                         '{0:s}; value = {1:s}.'.format(reason, str(value)))
        return ret_val

    def process(self):
        """Run continuously in the main thread."""
        t0 = _time.time()
        self.status
        tf = _time.time()
        dt = INTERVAL - (tf-t0)
        if dt > 0:
            _time.sleep(dt)
        else:
            _log.debug('App: check took {0:f}ms.'.format(dt*1000))

    def apply_corr(self, code):
        """Apply calculated kicks on the correctors."""
        if not self.orbit.correction_mode:
            self._update_log('ERR: Offline, cannot apply kicks.')
            return False
        if self._thread and self._thread.is_alive():
            self._update_log('ERR: AutoCorr or MeasRespMat is On.')
            return False
        if self._dtheta is None:
            self._update_log('ERR: Cannot Apply Kick. Calc Corr first.')
            return False
        _Thread(
            target=self._apply_corr, kwargs={'code': code},
            daemon=True).start()
        return True

    def calc_correction(self, value):
        """Calculate correction."""
        if self._thread and self._thread.is_alive():
            self._update_log('ERR: AutoCorr or MeasRespMat is On.')
            return False
        _Thread(target=self._calc_correction, daemon=True).start()
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
                self._update_log('ERR: AutoCorr is Already On.')
                return False
            if self._thread and self._thread.is_alive():
                self._update_log('ERR: Cannot Correct, Measuring RespMat.')
                return False
            self._update_log('Turning Auto Correction On.')
            self._auto_corr = value
            self._thread = _Thread(target=self._do_auto_corr,
                                   daemon=True)
            self._thread.start()
        elif value == _csorb.AutoCorr.Off:
            self._update_log('Turning Auto Correction Off.')
            self._auto_corr = value
        return True

    def set_auto_corr_frequency(self, value):
        self._auto_corr_freq = value
        self.run_callbacks('AutoCorrFreq-RB', value)
        return True

    def set_max_kick(self, plane, value):
        self._max_kick[plane] = float(value)
        self.run_callbacks('MaxKick'+plane.upper()+'-RB', float(value))

    def set_corr_factor(self, plane, value):
        self._corr_factor[plane] = value/100
        self._update_log(
            '{0:s} CorrFactor set to {1:6.2f}'.format(plane.upper(), value))
        self.run_callbacks('CorrFactor'+plane.upper()+'-RB', value)
        return True

    def set_respmat_kick(self, plane, value):
        self._meas_respmat_kick[plane] = value
        self.run_callbacks('MeasRespMatKick'+plane.upper()+'-RB', value)

    def _update_status(self):
        self._status = bool(
            self._correctors.status | self._matrix.status | self._orbit.status)
        self.run_callbacks('Status-Mon', self._status)

    def _apply_corr(self, code):
        nr_ch = self._const.NR_CH
        kicks = self._dtheta.copy()
        if code == _csorb.ApplyCorr.CH:
            kicks[nr_ch:] = 0
        elif code == _csorb.ApplyCorr.CV:
            kicks[:nr_ch] = 0
            kicks[-1] = 0
        elif code == _csorb.ApplyCorr.RF:
            kicks[:-1] = 0
        self._update_log(
            'Applying {0:s} kicks.'.format(_csorb.ApplyCorr._fields[code]))
        kicks = self._process_kicks(kicks)
        if any(kicks):
            self.correctors.apply_kicks(self._ref_corr_kicks + kicks)

    def _schedule_update(self, pvname, value, **kwargs):
        self._queue.add_callback(self._update_driver, pvname, value, **kwargs)

    def _update_driver(self, pvname, value, **kwargs):
        self._driver.setParam(pvname, value)
        self._driver.updatePV(pvname)

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
            self._update_log('ERR: No Measurement ocurring.')
            return False
        self._update_log('Aborting measurement.')
        self._measuring_respmat = False
        self._thread.join()
        self._update_log('Measurement aborted.')
        return True

    def _reset_meas_respmat(self):
        if self._measuring_respmat:
            self._update_log('Cannot Reset, Measurement in process.')
            return False
        self._update_log('Reseting measurement status.')
        self.run_callbacks('MeasRespMat-Mon', _csorb.MeasRespMatMon.Idle)
        return True

    def _start_meas_respmat(self):
        if self._measuring_respmat:
            self._update_log('ERR: Measurement already in process.')
            return False
        if self._thread and self._thread.is_alive():
            self._update_log('ERR: Cannot Measure, AutoCorr is On.')
            return False
        self._update_log('Starting RespMat measurement.')
        self._measuring_respmat = True
        self._thread = _Thread(target=self._do_meas_respmat, daemon=True)
        self._thread.start()
        return True

    def _do_meas_respmat(self):
        nr_corrs = self._const.NR_CORRS
        nr_bpms = self._const.NR_BPMS
        self.run_callbacks('MeasRespMat-Mon', _csorb.MeasRespMatMon.Measuring)
        mat = _np.zeros([2*nr_bpms, nr_corrs])
        orig_kicks = self.correctors.get_strength()
        for i in range(nr_corrs):
            if not self._measuring_respmat:
                self.run_callbacks(
                            'MeasRespMat-Mon', _csorb.MeasRespMatMon.Aborted)
                self.correctors.apply_kicks(orig_kicks)
                return
            self._update_log(
                    'Varying Corrector {0:d} of {1:d}'.format(i, nr_corrs))
            if i < self._const.NR_CH:
                delta = self._meas_respmat_kick['ch']
            elif i < nr_corrs - 1:
                delta = self._meas_respmat_kick['cv']
            else:
                delta = self._meas_respmat_kick['rf']
            kicks = orig_kicks.copy()
            kicks[i] += delta/2
            self.correctors.apply_kicks(kicks)
            orbp = self.orbit.get_orbit(True)
            kicks[i] += -delta
            self.correctors.apply_kicks(kicks)
            orbn = self.orbit.get_orbit(True)
            mat[:, i] = (orbp-orbn)/delta
        self.correctors.apply_kicks(orig_kicks)
        self._update_log('Measurement Completed.')
        self.set_respmat(list(mat.flatten()))
        self.run_callbacks('MeasRespMat-Mon', _csorb.MeasRespMatMon.Completed)
        self._measuring_respmat = False

    def _do_auto_corr(self):
        if not self.orbit.correction_mode:
            self._update_log('ERR: Cannot Auto Correct in Offline Mode')
            self.run_callbacks('AutoCorr-Sel', 0)
            self.run_callbacks('AutoCorr-Sts', 0)
            return
        self.run_callbacks('AutoCorr-Sts', 1)
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
                self._update_log(
                    'Warn: Auto Corr Loop took {0:6.2f}ms.'.format(dt*1000))
            dt = interval - dt
            if dt > 0:
                _time.sleep(dt)
        self._update_log('Auto Correction is Off.')
        self.run_callbacks('AutoCorr-Sts', 0)

    def _calc_correction(self):
        self._update_log('Getting the orbit.')
        orb = self.orbit.get_orbit()
        self._update_log('Calculating the kicks.')
        self._ref_corr_kicks = self.correctors.get_strength()
        self._dtheta = self.matrix.calc_kicks(orb)

    def _process_kicks(self, kicks):
        nr_ch = self._const.NR_CH
        kicks[:nr_ch] *= self._corr_factor['ch']
        kicks[nr_ch:-1] *= self._corr_factor['cv']
        kicks[-1] *= self._corr_factor['rf']

        max_kick_ch = max(abs(kicks[:nr_ch]))
        if max_kick_ch > self._max_kick['ch']:
            factor = self._max_kick['ch']/max_kick_ch
            kicks[:nr_ch] *= factor
            percent = self._corr_factor['ch'] * factor * 100
            self._update_log(
                'Warn: CH kick > MaxKickCH. Using {0:5.2f}%'.format(percent))
        max_kick_cv = max(abs(kicks[nr_ch:-1]))
        if max_kick_cv > self._max_kick['cv']:
            factor = self._max_kick['cv']/max_kick_cv
            kicks[nr_ch:-1] *= factor
            percent = self._corr_factor['cv'] * factor * 100
            self._update_log(
                'Warn: CV kick > MaxKickCV. Using {0:5.2f}%'.format(percent))
        if abs(kicks[-1]) > self._max_kick['rf']:
            factor = self._max_kick['rf'] / abs(kicks[-1])
            kicks[-1] *= factor
            percent = self._corr_factor['rf'] * factor * 100
            self._update_log(
                'Warn: RF kick > MaxKickRF. Using {0:5.2f}%'.format(percent))
        return kicks
