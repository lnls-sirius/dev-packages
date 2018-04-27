"""Main module of AS-AP-TuneCorr IOC."""

import time as _time
import epics as _epics
import siriuspy as _siriuspy
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from siriuspy.csdevice.opticscorr import Const as _Const
from as_ap_opticscorr.opticscorr_utils import (
        OpticsCorr as _OpticsCorr,
        get_config_name as _get_config_name,
        set_config_name as _set_config_name)
import as_ap_opticscorr.tune.pvs as _pvs

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be
#      easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive'
#      (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes,
#      suffixes, etc)


# Constants
_ALLSET = 0x1f
_ALLCLR_SYNCON = 0x00
_ALLCLR_SYNCOFF = 0x10


class App:
    """Main application for handling tune correction."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _pvs.print_banner_and_save_pv_list()
        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()
        self._ACC = _pvs.get_pvs_section()
        self._QFAMS = list(_pvs.get_corr_fams())

        self._driver = driver

        self._delta_tunex = 0.0
        self._delta_tuney = 0.0

        self._status = _ALLSET
        self._qfam_check_connection = len(self._QFAMS)*[0]
        self._qfam_check_pwrstate_sts = len(self._QFAMS)*[0]
        self._qfam_check_opmode_sts = len(self._QFAMS)*[-1]
        self._qfam_check_ctrlmode_mon = len(self._QFAMS)*[1]

        self._corr_factor = 0.0
        self._set_new_refkl_cmd_count = 0
        self._apply_corr_cmd_count = 0
        self._config_ma_cmd_count = 0
        self._lastcalc_deltakl = len(self._QFAMS)*[0]

        self._qfam_kl_rb = len(self._QFAMS)*[0]

        if self._ACC.lower() == 'si':
            self._corr_method = _Const.CorrMeth.Proportional
            self._sync_corr = _Const.SyncCorr.Off
            self._config_timing_cmd_count = 0
            self._timing_check_config = 6*[0]
        else:
            self._corr_method = _Const.CorrMeth.Additional
            self._sync_corr = _Const.SyncCorr.Off

        # Get focusing and defocusing families
        qfam_focusing = []
        qfam_defocusing = []
        for fam in self._QFAMS:
            if 'QF' in fam:
                qfam_focusing.append(fam)
            else:
                qfam_defocusing.append(fam)

        # Initialize correction parameters from local file and configdb
        config_name = _get_config_name(acc=self._ACC.lower(),
                                       opticsparam='tune')
        [done, corrparams] = self._get_corrparams(config_name)
        if done:
            self.driver.setParam('ConfigName-SP', config_name)
            self.driver.setParam('ConfigName-RB', config_name)
            self._nominal_matrix = corrparams[0]
            self.driver.setParam('RespMat-Mon', self._nominal_matrix)
            self._qfam_nomkl = corrparams[1]
            self.driver.setParam('NominalKL-Mon', self._qfam_nomkl)
            self._opticscorr = _OpticsCorr(
                magnetfams_ordering=self._QFAMS,
                nominal_matrix=self._nominal_matrix,
                nominal_intstrengths=self._qfam_nomkl,
                nominal_opticsparam=[0.0, 0.0],
                magnetfams_focusing=qfam_focusing,
                magnetfams_defocusing=qfam_defocusing)
        else:
            raise Exception("Could not read correction parameters from "
                            "configdb.")

        # Connect to Quadrupoles Families
        self._qfam_kl_sp_pvs = {}
        self._qfam_kl_rb_pvs = {}
        self._qfam_pwrstate_sel_pvs = {}
        self._qfam_pwrstate_sts_pvs = {}
        self._qfam_opmode_sel_pvs = {}
        self._qfam_opmode_sts_pvs = {}
        self._qfam_ctrlmode_mon_pvs = {}
        self._qfam_refkl = {}

        for fam in self._QFAMS:
            self._qfam_kl_sp_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':KL-SP')

            self._qfam_refkl[fam] = 0
            self._qfam_kl_rb_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':KL-RB',
                callback=[self._callback_init_refkl,
                          self._callback_estimate_deltatune],
                connection_callback=self._connection_callback_qfam_kl_rb)

            self._qfam_pwrstate_sel_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':PwrState-Sel')
            self._qfam_pwrstate_sts_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':PwrState-Sts',
                callback=self._callback_qfam_pwrstate_sts)

            self._qfam_opmode_sel_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':OpMode-Sel')
            self._qfam_opmode_sts_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':OpMode-Sts',
                callback=self._callback_qfam_opmode_sts)

            self._qfam_ctrlmode_mon_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':CtrlMode-Mon',
                callback=self._callback_qfam_ctrlmode_mon)

        # Connect to Timing
        if self._ACC == 'SI':
            self._timing_quads_state_sel = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Quads:State-Sel')
            self._timing_quads_state_sts = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Quads:State-Sts',
                callback=self._callback_timing_state)

            self._timing_quads_evgparam_sel = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Quads:EVGParam-Sel')
            self._timing_quads_evgparam_sts = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Quads:EVGParam-Sts',
                callback=self._callback_timing_state)

            self._timing_quads_pulses_sp = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Quads:Pulses-SP')
            self._timing_quads_pulses_rb = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Quads:Pulses-RB',
                callback=self._callback_timing_state)

            self._timing_quads_duration_sp = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Quads:Duration-SP')
            self._timing_quads_duration_rb = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-Quads:Duration-RB',
                callback=self._callback_timing_state)

            self._timing_evg_tunesmode_sel = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-EVG:TunesMode-Sel')
            self._timing_evg_tunemode_sts = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-EVG:TunesMode-Sts',
                callback=self._callback_timing_state)

            self._timing_evg_tunesdelay_sp = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-EVG:TunesDelay-SP')
            self._timing_evg_tunesdelay_rb = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-EVG:TunesDelay-RB',
                callback=self._callback_timing_state)

            self._timing_evg_tunesexttrig_cmd = _epics.PV(
                self._PREFIX_VACA+'SI-Glob:TI-EVG:TunesExtTrig-Cmd')

        self.driver.setParam('Log-Mon', 'Started.')
        self.driver.updatePVs()

    @staticmethod
    def init_class():
        """Init class."""
        App.pvs_database = _pvs.get_pvs_database()

    @property
    def driver(self):
        """Return driver."""
        return self._driver

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        return None

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'DeltaTuneX-SP':
            self._delta_tunex = value
            self._calc_deltakl()
            self.driver.updatePVs()
            status = True

        elif reason == 'DeltaTuneY-SP':
            self._delta_tuney = value
            self._calc_deltakl()
            self.driver.updatePVs()
            status = True

        elif reason == 'ApplyCorr-Cmd':
            done = self._apply_corr()
            if done:
                self._apply_corr_cmd_count += 1
                self.driver.setParam('ApplyCorr-Cmd',
                                     self._apply_corr_cmd_count)
                self.driver.updatePVs()

        elif reason == 'ConfigName-SP':
            [done, corrparams] = self._get_corrparams(value)
            if done:
                _set_config_name(acc=self._ACC.lower(),
                                 opticsparam='tune',
                                 config_name=value)
                self.driver.setParam('ConfigName-RB', value)
                self._nominal_matrix = corrparams[0]
                self.driver.setParam('RespMat-Mon', self._nominal_matrix)
                self._qfam_nomkl = corrparams[1]
                self.driver.setParam('NominalKL-Mon', self._qfam_nomkl)
                self._opticscorr.nominal_matrix = self._nominal_matrix
                self._opticscorr.nominal_intstrengths = self._qfam_nomkl
                self._calc_deltakl()
                self.driver.setParam('Log-Mon',
                                     'Updated correction parameters.')
                self.driver.updatePVs()
                status = True
            else:
                self.driver.setParam(
                    'Log-Mon', 'ERR:Configuration not found in configdb.')
                self.driver.updatePVs()

        elif reason == 'CorrMeth-Sel':
            if value != self._corr_method:
                self._corr_method = value
                self.driver.setParam('CorrMeth-Sts', value)
                self._calc_deltakl()
                self.driver.updatePVs()
                status = True

        elif reason == 'CorrFactor-SP':
            if value != self._corr_factor:
                self._corr_factor = value
                self.driver.setParam('CorrFactor-RB', value)
                self._calc_deltakl()
                self.driver.updatePVs()
                status = True

        elif reason == 'SyncCorr-Sel':
            if value != self._sync_corr:
                self._sync_corr = value

                done = self._config_ma()
                if done:
                    self._config_ma_cmd_count += 1
                    self.driver.setParam('ConfigMA-Cmd',
                                         self._config_ma_cmd_count)

                if value == 1:
                    done = self._config_timing()
                    if done:
                        self._config_timing_cmd_count += 1
                        self.driver.setParam('ConfigTiming-Cmd',
                                             self._config_timing_cmd_count)

                if (self._status & 0x1) == 0:
                    for fam in self._QFAMS:
                        fam_index = self._QFAMS.index(fam)
                        self._qfam_check_opmode_sts[fam_index] = (
                            self._qfam_opmode_sts_pvs[fam].value)

                    val = (1 if any(op != value for op in
                                    self._qfam_check_opmode_sts) else 0)
                else:
                    val = 1

                self._status = _siriuspy.util.update_integer_bit(
                    integer=self._status, number_of_bits=5, value=val, bit=2)

                self.driver.setParam('Status-Mon', self._status)
                self.driver.setParam('SyncCorr-Sts', self._sync_corr)
                self.driver.updatePVs()
                status = True

        elif reason == 'ConfigMA-Cmd':
            done = self._config_ma()
            if done:
                self._config_ma_cmd_count += 1
                self.driver.setParam('ConfigMA-Cmd',
                                     self._config_ma_cmd_count)
                self.driver.updatePVs()

        elif reason == 'ConfigTiming-Cmd':
            done = self._config_timing()
            if done:
                self._config_timing_cmd_count += 1
                self.driver.setParam('ConfigTiming-Cmd',
                                     self._config_timing_cmd_count)
                self.driver.updatePVs()

        elif reason == 'SetNewRefKL-Cmd':
            self._update_ref()
            self._set_new_refkl_cmd_count += 1
            self.driver.setParam('SetNewRefKL-Cmd',
                                 self._set_new_refkl_cmd_count)
            self.driver.updatePVs()  # in case PV states change.

        return status  # return True to invoke super().write of PCASDriver

    def _get_corrparams(self, config_name):
        """Get response matrix from configurations database."""
        cs = _ConfigService()
        querry = cs.get_config(self._ACC.lower()+'_tunecorr_params',
                               config_name)
        querry_result = querry['code']

        if querry_result == 200:
            done = True
            params = querry['result']['value']

            nominal_matrix = [item for sublist in params['matrix']
                              for item in sublist]
            nominal_kl = params['nominal KLs']
            return [done, [nominal_matrix, nominal_kl]]
        else:
            done = False
            return [done, []]

    def _calc_deltakl(self):
        if self._corr_method == _Const.CorrMeth.Proportional:
            lastcalc_deltakl = self._opticscorr.calculate_delta_intstrengths(
                method=0, grouping='2knobs',
                delta_opticsparam=[self._delta_tunex, self._delta_tuney])
        else:
            lastcalc_deltakl = self._opticscorr.calculate_delta_intstrengths(
                method=1, grouping='2knobs',
                delta_opticsparam=[self._delta_tunex, self._delta_tuney])

        self.driver.setParam('Log-Mon', 'Calculated KL values.')

        self._lastcalc_deltakl = lastcalc_deltakl
        for fam in self._QFAMS:
            fam_index = self._QFAMS.index(fam)
            self.driver.setParam(
                'DeltaKL' + fam + '-Mon',
                (self._corr_factor/100) * self._lastcalc_deltakl[fam_index])
        self.driver.updatePVs()

    def _apply_corr(self):
        if ((self._status == _ALLCLR_SYNCOFF and
                self._sync_corr == _Const.SyncCorr.Off) or
                self._status == _ALLCLR_SYNCON):
            for fam in self._qfam_kl_sp_pvs:
                fam_index = self._QFAMS.index(fam)
                pv = self._qfam_kl_sp_pvs[fam]
                pv.put(self._qfam_refkl[fam] + (self._corr_factor/100) *
                       self._lastcalc_deltakl[fam_index])
            self.driver.setParam('Log-Mon', 'Applied correction.')
            self.driver.updatePVs()

            if self._sync_corr == _Const.SyncCorr.On:
                self._timing_evg_tunesexttrig_cmd.put(0)
                self.driver.setParam('Log-Mon', 'Generated trigger.')
                self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon', 'ERR:ApplyCorr-Cmd failed.')
            self.driver.updatePVs()
        return False

    def _update_ref(self):
        if (self._status & 0x1) == 0:  # Check connection
            # updates reference
            for fam in self._QFAMS:
                value = self._qfam_kl_rb_pvs[fam].get()
                if value is None:
                    return
                self._qfam_refkl[fam] = value
                self.driver.setParam('RefKL' + fam + '-Mon',
                                     self._qfam_refkl[fam])

                fam_index = self._QFAMS.index(fam)
                self._lastcalc_deltakl[fam_index] = 0
                self.driver.setParam('DeltaKL' + fam + '-Mon', 0)

            # the deltas from new kl references are zero
            self._delta_tunex = 0
            self._delta_tuney = 0
            self.driver.setParam('DeltaTuneX-SP', self._delta_tunex)
            self.driver.setParam('DeltaTuneY-SP', self._delta_tuney)
            delta_tunex, delta_tuney = self._estimate_current_deltatune()
            self.driver.setParam('DeltaTuneX-RB', delta_tunex)
            self.driver.setParam('DeltaTuneY-RB', delta_tuney)

            self.driver.setParam('Log-Mon', 'Updated KL references.')
        else:
            self.driver.setParam('Log-Mon',
                                 'ERR:Some magnet family is disconnected.')
        self.driver.updatePVs()

    def _estimate_current_deltatune(self):
        qfam_deltakl = len(self._QFAMS)*[0]
        for fam in self._QFAMS:
            fam_index = self._QFAMS.index(fam)
            qfam_deltakl[fam_index] = (
                self._qfam_kl_rb[fam_index] - self._qfam_refkl[fam])
        return self._opticscorr.calculate_opticsparam(qfam_deltakl)

    def _callback_init_refkl(self, pvname, value, cb_info, **kws):
        """Initialize RefKL-Mon pvs and remove this callback."""
        ps = pvname.split(self._PREFIX_VACA)[1]
        fam = ps.split(':')[1].split('-')[1]

        # Get reference
        self._qfam_refkl[fam] = value
        self.driver.setParam('RefKL' + fam + '-Mon', self._qfam_refkl[fam])

        # Remove callback
        cb_info[1].remove_callback(cb_info[0])

    def _connection_callback_qfam_kl_rb(self, pvname, conn, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        if not conn:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' disconnected.')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._QFAMS.index(fam)
        self._qfam_check_connection[fam_index] = (1 if conn else 0)

        # Change the first bit of correction status
        val = (1 if any(q == 0 for q in self._qfam_check_connection) else 0)
        self._status = _siriuspy.util.update_integer_bit(
            integer=self._status, number_of_bits=5, value=val, bit=0)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_estimate_deltatune(self, pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._QFAMS.index(fam)
        self._qfam_kl_rb[fam_index] = value

        delta_tunex, delta_tuney = self._estimate_current_deltatune()
        self.driver.setParam('DeltaTuneX-RB', delta_tunex)
        self.driver.setParam('DeltaTuneY-RB', delta_tuney)
        self.driver.updatePVs()

    def _callback_qfam_pwrstate_sts(self, pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        if value == 0:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Off.')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._QFAMS.index(fam)
        self._qfam_check_pwrstate_sts[fam_index] = value

        # Change the second bit of correction status
        val = (1 if any(q == 0 for q in self._qfam_check_pwrstate_sts) else 0)
        self._status = _siriuspy.util.update_integer_bit(
            integer=self._status, number_of_bits=5, value=val, bit=1)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_qfam_opmode_sts(self, pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        self.driver.setParam('Log-Mon', 'WARN:'+ps+' changed.')
        self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._QFAMS.index(fam)
        self._qfam_check_opmode_sts[fam_index] = value

        # Change the third bit of correction status
        opmode = self._sync_corr
        val = (1 if any(s != opmode for s in self._qfam_check_opmode_sts)
               else 0)
        self._status = _siriuspy.util.update_integer_bit(
            integer=self._status, number_of_bits=5, value=val, bit=2)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_qfam_ctrlmode_mon(self,  pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        if value == 1:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Local.')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._QFAMS.index(fam)
        self._qfam_check_ctrlmode_mon[fam_index] = value

        # Change the fourth bit of correction status
        val = (1 if any(q == 1 for q in self._qfam_check_ctrlmode_mon)
               else 0)
        self._status = _siriuspy.util.update_integer_bit(
            integer=self._status, number_of_bits=5, value=val, bit=3)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_timing_state(self, pvname, value, **kws):
        if 'Quads:State' in pvname:
            self._timing_check_config[0] = value  # Enbl
        elif 'Quads:EVGParam' in pvname:
            self._timing_check_config[1] = (1 if value == 1 else 0)  # Tunes
        elif 'Quads:Pulses' in pvname:
            self._timing_check_config[2] = (1 if value == 1 else 0)  # 1 pulse
        elif 'Quads:Duration' in pvname:
            self._timing_check_config[3] = (1 if value == 0.15 else 0)  # 150us
        elif 'TunesMode' in pvname:
            self._timing_check_config[4] = (1 if value == 3 else 0)  # External
        elif 'TunesDelay' in pvname:
            self._timing_check_config[5] = (1 if value == 0 else 0)  # 0s

        # Change the fifth bit of correction status
        val = (1 if any(index == 0 for index in self._timing_check_config)
               else 0)
        self._status = _siriuspy.util.update_integer_bit(
            integer=self._status, number_of_bits=5, value=val, bit=4)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _config_ma(self):
        opmode = self._sync_corr
        for fam in self._QFAMS:
            if self._qfam_pwrstate_sel_pvs[fam].connected:
                self._qfam_pwrstate_sel_pvs[fam].put(1)
                self._qfam_opmode_sel_pvs[fam].put(opmode)
            else:
                self.driver.setParam('Log-Mon',
                                     'ERR:' + fam + ' is disconnected.')
                self.driver.updatePVs()
                return False
        self.driver.setParam('Log-Mon', 'Sent configuration to quadrupoles.')
        self.driver.updatePVs()
        return True

    def _config_timing(self):
        if not any(pv.connected is False for pv in [
                              self._timing_quads_state_sel,
                              self._timing_quads_evgparam_sel,
                              self._timing_quads_pulses_sp,
                              self._timing_quads_duration_sp,
                              self._timing_evg_tunesmode_sel,
                              self._timing_evg_tunesdelay_sp]):
            self._timing_quads_state_sel.put(1)
            self._timing_quads_evgparam_sel.put(1)
            self._timing_quads_pulses_sp.put(1)
            self._timing_quads_duration_sp.put(0.15)
            self._timing_evg_tunesmode_sel.put(3)
            self._timing_evg_tunesdelay_sp.put(0)
            self.driver.setParam('Log-Mon', 'Sent configuration to timing.')
            self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon',
                                 'ERR:Some timing PV is disconnected.')
            self.driver.updatePVs()
            return False
