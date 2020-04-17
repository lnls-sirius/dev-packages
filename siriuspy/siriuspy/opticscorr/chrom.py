"""Main module of AS-AP-ChromCorr IOC."""

import time as _time
from threading import Thread as _Thread
import numpy as _np
from epics import PV as _PV

from ..envars import VACA_PREFIX as _vaca_prefix
from ..namesys import SiriusPVName as _SiriusPVName

from .csdev import Const as _Const
from .base import BaseApp as _BaseApp

_MOM_COMPACT = 1.68e-4
_MAX_DELTA_RF_FREQ = 20.0


class ChromCorrApp(_BaseApp):
    """Main application for handling chromaticity correction."""

    _optics_param = 'chrom'

    def __init__(self, acc):
        """Class constructor."""
        super().__init__(acc)

        # consts
        self._chrom_sp = 2*[0.0]
        self._chrom_mon = 2*[0.0]
        self._chrom_est = 2*[0.0]

        if self._acc == 'SI':
            self._measuring_chrom = False
            self._meas_chrom_status = _Const.MeasMon.Idle
            self._meas_chrom_lastcomm = _Const.MeasCmd.Reset
            self._meas_chrom_dfreq_rf = 200.0
            self._meas_chrom_wait_tune = 5.0
            self._meas_chrom_nrsteps = 8

            self._meas_config_dsl_sf = 0.1000
            self._meas_config_dsl_sd = 0.1000

        # Connect to Sextupoles Families
        self._lastcalc_sl = {fam: 0 for fam in self._psfams}
        for fam in self._psfams:
            self._psfam_intstr_rb_pvs[fam].add_callback(
                self._callback_estimate_chrom)

        if self._acc == 'SI':
            # Connect to SI RF
            self._rf_freq_sp_pv = _PV(
                _vaca_prefix+'RF-Gen:GeneralFreq-SP', connection_timeout=0.05)
            self._rf_freq_rb_pv = _PV(
                _vaca_prefix+'RF-Gen:GeneralFreq-RB', connection_timeout=0.05)

        self.map_pv2write.update({
            'ChromX-SP': self.set_chrom_x,
            'ChromY-SP': self.set_chrom_y,
            'MeasChromDeltaFreqRF-SP': self.set_meas_chrom_dfreq_rf,
            'MeasChromWaitTune-SP': self.set_meas_chrom_wait_tune,
            'MeasChromNrSteps-SP': self.set_meas_chrom_nrsteps,
            'MeasChrom-Cmd': self.cmd_meas_chrom,
            'MeasConfigDeltaSLSF-SP': self.set_meas_config_dsl_sf,
            'MeasConfigDeltaSLSD-SP': self.set_meas_config_dsl_sd,
        })

    def update_corrparams(self):
        """Set initial correction parameters PVs values."""
        self.run_callbacks('RespMat-Mon', self._nominal_matrix)
        self.run_callbacks('NominalSL-Mon', self._psfam_nom_intstr)
        self.run_callbacks('NominalChrom-Mon', self._nominal_opticsparam)

    def process(self, interval):
        """Sleep."""
        t_ini = _time.time()
        limit_names = {
            'hilim': 'upper_disp_limit', 'lolim': 'lower_disp_limit',
            'high': 'upper_alarm_limit', 'low': 'lower_alarm_limit',
            'hihi': 'upper_warning_limit', 'lolo': 'lower_warning_limit'}
        if (self._status & 0x1) == 0:  # Check connection
            for fam in self._psfams:
                data = self._psfam_intstr_rb_pvs[fam].get_ctrlvars()
                if self._psfam_intstr_rb_pvs[fam].upper_disp_limit is not None:
                    lis = {k: data[v] for k, v in limit_names.items()}
                    self.run_callbacks('SL'+fam+'-Mon', info=lis, field='info')
        dtime = interval - (_time.time() - t_ini)
        _time.sleep(max(dtime, 0))

    # ------ handle pv write methods -------

    def set_chrom_x(self, value):
        """Set ChromX."""
        self._chrom_sp[0] = value
        self.run_callbacks('ChromX-RB', value)
        self._calc_intstrength()
        return True

    def set_chrom_y(self, value):
        """Set ChromY."""
        self._chrom_sp[1] = value
        self.run_callbacks('ChromY-RB', value)
        self._calc_intstrength()
        return True

    def set_meas_chrom_dfreq_rf(self, value):
        """Set MeasChromDeltaFreqRF."""
        if value == self._meas_chrom_dfreq_rf:
            return False
        self._meas_chrom_dfreq_rf = value
        self.run_callbacks('MeasChromDeltaFreqRF-RB', value)
        return True

    def set_meas_chrom_wait_tune(self, value):
        """Set MeasChromWaitTune."""
        if value == self._meas_chrom_wait_tune:
            return False
        self._meas_chrom_wait_tune = value
        self.run_callbacks('MeasChromWaitTune-RB', value)
        return True

    def set_meas_chrom_nrsteps(self, value):
        """Set MeasChromNrSteps."""
        if value == self._meas_chrom_nrsteps:
            return False
        self._meas_chrom_nrsteps = value
        self.run_callbacks('MeasChromNrSteps-RB', value)
        return True

    def cmd_meas_chrom(self, value):
        """MeasChrom command."""
        if value == _Const.MeasCmd.Start:
            status = self._start_meas_chrom()
        elif value == _Const.MeasCmd.Stop:
            status = self._stop_meas_chrom()
        elif value == _Const.MeasCmd.Reset:
            status = self._reset_meas_chrom()
        if status:
            self._meas_chrom_lastcomm = value
        return status

    def set_meas_config_dsl_sf(self, value):
        """Set MeasConfigDeltaSLSF."""
        if value == self._meas_config_dsl_sf:
            return False
        self._meas_config_dsl_sf = value
        self.run_callbacks('MeasConfigDeltaSLSF-RB', value)
        return True

    def set_meas_config_dsl_sd(self, value):
        """Set MeasConfigDeltaSLSD."""
        if value == self._meas_config_dsl_sd:
            return False
        self._meas_config_dsl_sd = value
        self.run_callbacks('MeasConfigDeltaSLSD-RB', value)
        return True

    # ---------- auxiliar methods ----------

    def _handle_corrparams_2_read(self, params):
        """Edit correction params."""
        nom_matrix = [item for sublist in params['matrix'] for item in sublist]
        nom_sl = params['nominal SLs']
        nom_chrom = params['nominal chrom']
        return nom_matrix, nom_sl, nom_chrom

    def _handle_corrparams_2_save(self):
        matrix = _np.array(self._nominal_matrix)
        matrix = _np.reshape(matrix, [2, len(self._psfams)])

        value = {'matrix': matrix,
                 'nominal SLs': self._psfam_nom_intstr,
                 'nominal chrom': self._nominal_opticsparam}
        return value

    def _calc_intstrength(self):
        delta_chromx = self._chrom_sp[0]-self._chrom_est[0]
        delta_chromy = self._chrom_sp[1]-self._chrom_est[1]

        method = 0 \
            if self._corr_method == _Const.CorrMeth.Proportional \
            else 1
        grouping = '2knobs' \
            if self._corr_group == _Const.CorrGroup.TwoKnobs \
            else 'svd'
        lastcalc_deltasl = self._opticscorr.calculate_delta_intstrengths(
            method=method, grouping=grouping,
            delta_opticsparam=[delta_chromx, delta_chromy])

        for fam in self._psfams:
            fam_idx = self._psfams.index(fam)
            sl_now = self._psfam_intstr_rb_pvs[fam].get()
            if sl_now is None:
                self.run_callbacks(
                    'Log-Mon',
                    'ERR: Received a None value from {}'.format(fam))
                return False
            self._lastcalc_sl[fam] = sl_now + lastcalc_deltasl[fam_idx]
            self.run_callbacks('SL'+fam+'-Mon', self._lastcalc_sl[fam])

        self.run_callbacks('Log-Mon', 'Calculated SL values.')
        return True

    def _apply_corr(self):
        if self._is_status_ok():
            self._apply_intstrength(self._lastcalc_sl)
            self.run_callbacks('Log-Mon', 'Applied correction.')

            if self._sync_corr == _Const.SyncCorr.On:
                self._event_exttrig_cmd.put(0)
                self.run_callbacks('Log-Mon', 'Generated trigger.')
            return True

        self.run_callbacks('Log-Mon', 'ERR:ApplyDelta-Cmd failed.')
        return False

    def _get_optics_param(self):
        """Return optics parameter."""
        sts = self._meas_chrom()
        return sts, self._chrom_mon

    def _get_delta_intstrength(self, fam):
        if 'SL' in fam:
            deltasl = self._meas_config_dsl_sf
        else:
            deltasl = self._meas_config_dsl_sd
        return deltasl

    def _set_rf_freq(self, value):
        freq_curr = self._get_rf_freq()
        delta = abs(freq_curr - value)

        npoints = int(round(delta/_MAX_DELTA_RF_FREQ)) + 2
        freq_span = _np.linspace(freq_curr, value, npoints)[1:]

        for freq in freq_span:
            self._rf_freq_sp_pv.put(freq, wait=False)
            _time.sleep(1.0)
        self._rf_freq_sp_pv.value = value

    def _get_rf_freq(self):
        """Get RF Frequnecy."""
        if not self._rf_freq_rb_pv.connected:
            return 0.0
        return self._rf_freq_rb_pv.value

    def _start_meas_chrom(self):
        """Start chromaticity measurement."""
        if self._measuring_chrom:
            log_msg = 'ERR: Chrom measurement already in progress!'
            cont = False
        elif not self._tune_x_pv.connected or not self._tune_y_pv.connected:
            log_msg = 'ERR: Cannot measure, tune PVs not connected!'
            cont = False
        elif not self._rf_freq_sp_pv.connected:
            log_msg = 'ERR: Cannot measure, RF PVs not connected!'
            cont = False
        elif not self._is_storedebeam:
            log_msg = 'ERR: Cannot measure, there is no stored beam!'
            cont = False
        if not cont:
            self.run_callbacks('Log-Mon', log_msg)
            return False

        thread = _Thread(target=self._meas_chrom, daemon=True)
        thread.start()
        return True

    def _stop_meas_chrom(self):
        """Stop chromaticity measurement."""
        if not self._measuring_chrom:
            self.run_callbacks(
                'Log-Mon', 'ERR: No chrom measurement occuring!')
            return False
        self.run_callbacks('Log-Mon', 'Aborting chrom measurement!')
        self._measuring_chrom = False
        return True

    def _reset_meas_chrom(self):
        """Reset chromaticity measurement."""
        if self._measuring_chrom:
            self.run_callbacks(
                'Log-Mon', 'ERR: Status not reset, measure in progress!')
            return False
        self.run_callbacks(
            'Log-Mon', 'Reseting chrom measurement status!')
        self._meas_chrom_status = _Const.MeasMon.Idle
        self.run_callbacks('MeasChromStatus-Mon', self._meas_chrom_status)
        return True

    def _meas_chrom(self):
        """Measure chromaticities."""
        self._meas_chrom_status = _Const.MeasMon.Measuring
        self.run_callbacks('MeasChromStatus-Mon', self._meas_chrom_status)

        self._measuring_chrom = True
        self.run_callbacks('Starting chrom measurement!')

        _, data = self._get_tunes()
        tunex0, tuney0 = data

        freq0 = self._get_rf_freq()
        frequencies = _np.linspace(
            freq0-self._meas_chrom_dfreq_rf/2,
            freq0+self._meas_chrom_dfreq_rf/2,
            self._meas_chrom_nrsteps)
        freq_list = list()
        tunex_list, tuney_list = list(), list()

        aborted = False
        for value in frequencies:
            if not self._measuring_chrom:
                log_msg = 'Stoped chrom measurement!'
                aborted = True
            elif not self._is_storedebeam:
                log_msg = 'ERR: Stoping chrom measurement, '\
                          'there is no stored beam!'
                aborted = True
            elif not self._tune_x_pv.connected or \
                    not self._tune_y_pv.connected:
                log_msg = 'ERR: Stoping chrom measurement, '\
                          'tune PVs not connected!'
                aborted = True
            elif not self._rf_freq_sp_pv.connected:
                log_msg = 'ERR: Stoping chrom measurement, '\
                          'RF PVs not connected!'
                aborted = True
            if aborted:
                break

            self._set_rf_freq(value)
            freq = self._get_rf_freq()
            freq_list.append(freq)
            self.run_callbacks(
                'Log-Mon', 'Delta RF: {} Hz'.format((freq-freq0)))

            _time.sleep(self._meas_chrom_wait_tune)
            sts, data = self._get_tunes()
            if sts:
                tunex, tuney = data
                tunex_list.append(tunex)
                tuney_list.append(tuney)
                self.run_callbacks(
                    'Log-Mon', 'Delta Tune X: {}'.format(
                        (tunex_list[-1]-tunex0)))
                self.run_callbacks(
                    'Log-Mon', 'Delta Tune Y: {}'.format(
                        (tuney_list[-1]-tuney0)))
            else:
                log_msg = 'ERR: Could not measure tune!'
                aborted = True
                break

        self.run_callbacks('Log-Mon', 'Restoring RF frequency...')
        self._set_rf_freq(freq0)
        self.run_callbacks('Log-Mon', 'RF frequency restored!')

        if aborted:
            self._meas_chrom_status = _Const.MeasMon.Aborted
        else:
            den = -(_np.array(freq) - freq0)/freq0/_MOM_COMPACT
            tunex_array = _np.array(tunex_list)
            tuney_array = _np.array(tuney_list)

            self._chrom_mon[0], _ = _np.polyfit(
                den, tunex_array, deg=1, cov=True)
            self._chrom_mon[1], _ = _np.polyfit(
                den, tuney_array, deg=1, cov=True)

            self.run_callbacks('MeasChromX-Mon', self._chrom_mon[0])
            self.run_callbacks('MeasChromY-Mon', self._chrom_mon[1])

            self._meas_chrom_status = _Const.MeasMon.Completed
            log_msg = 'Chromaticity measurement completed!'

        self.run_callbacks('MeasChromStatus-Mon', self._meas_chrom_status)
        self._measuring_config = False
        self.run_callbacks('Log-Mon', log_msg)
        return not aborted

    # ---------- callbacks ----------

    def _callback_estimate_chrom(self, pvname, value, **kws):
        if value is None:
            return
        fam = _SiriusPVName(pvname).dev
        self._psfam_intstr_rb[fam] = value

        sfam_deltasl = len(self._psfams)*[0]
        for fam in self._psfams:
            fam_idx = self._psfams.index(fam)
            sfam_deltasl[fam_idx] = \
                self._psfam_intstr_rb[fam] - self._psfam_nom_intstr[fam_idx]

        self._chrom_est = self._opticscorr.calculate_opticsparam(sfam_deltasl)
        self.run_callbacks('ChromX-Mon', self._chrom_est[0])
        self.run_callbacks('ChromY-Mon', self._chrom_est[1])
