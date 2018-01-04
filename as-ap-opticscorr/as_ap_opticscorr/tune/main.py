"""Main module of AS-AP-TuneCorr IOC."""

import time as _time
import numpy as _np
import epics as _epics
import siriuspy as _siriuspy
from as_ap_opticscorr.opticscorr_utils import OpticsCorr
from as_ap_opticscorr.opticscorr_utils import read_corrparams, save_corrparams
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
        self._QFAMS = _pvs.get_corr_fams()

        self._driver = driver

        self._status = _ALLSET
        self._qfam_check_connection = len(self._QFAMS)*[0]
        self._qfam_check_pwrstate_sts = len(self._QFAMS)*[0]
        self._qfam_check_opmode_sts = len(self._QFAMS)*[-1]
        self._qfam_check_ctrlmode_mon = len(self._QFAMS)*[1]

        self._corr_factor = 0.0
        self._set_new_refkl_cmd_count = 0
        self._config_qfam_ps_cmd_count = 0
        self._apply_deltakl_cmd_count = 0
        self._lastcalcd_deltakl = len(self._QFAMS)*[0]

        self._qfam_kl_rb = len(self._QFAMS)*[0]

        self._sync_corr = 0
        self._sync_corr_cmd_count = 0
        self._config_timing_cmd_count = 0
        self._timing_check_config = 6*[0]

        # Initialize correction parameters from local file
        self._opticscorr = OpticsCorr()

        # Using grouped and proportional method, the number of famlies is 2:
        # Focusing and Defocusing
        corrmat, nomkl = self._get_corrparams()

        if self._ACC == 'SI':
            self._qfam_nomkl = nomkl
            self.driver.setParam('NominalKL-SP', self._qfam_nomkl)
            self.driver.setParam('NominalKL-RB', self._qfam_nomkl)
            self._corr_method = 0
            corrmat = self._calc_matrix(corrmat)
        else:
            self._qfam_nomkl = None
            self._corr_method = 1

        self._mat, _ = self._opticscorr.set_corr_mat(2, corrmat)
        self.driver.setParam('CorrMat-SP', self._mat)
        self.driver.setParam('CorrMat-RB', self._mat)

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

        self._delta_tunex = 0
        self._delta_tuney = 0
        self._lastcalcd_deltakl = len(self._QFAMS)*[0]

        # Connect to Timing
        self._timing_quads_state_sel = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Quads:State-Sel')
        self._timing_quads_state_sts = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Quads:State-Sts',
            callback=self._callback_timing_state)

        self._timing_quads_evgparam_sel = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Quads:EVGParam-Sel')
        self._timing_quads_evgparam_sts = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Quads:EVGParam-Sts',
            callback=self._callback_timing_state)

        self._timing_quads_pulses_sp = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Quads:Pulses-SP')
        self._timing_quads_pulses_rb = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Quads:Pulses-RB',
            callback=self._callback_timing_state)

        self._timing_quads_duration_sp = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Quads:Duration-SP')
        self._timing_quads_duration_rb = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Quads:Duration-RB',
            callback=self._callback_timing_state)

        self._timing_evg_tunesmode_sel = _epics.PV(
            self._PREFIX_VACA+'AS-Glob:TI-EVG:'+self._ACC+'TunesMode-Sel')
        self._timing_evg_tunemode_sts = _epics.PV(
            self._PREFIX_VACA+'AS-Glob:TI-EVG:'+self._ACC+'TunesMode-Sts',
            callback=self._callback_timing_state)

        self._timing_evg_tunesdelay_sp = _epics.PV(
            self._PREFIX_VACA+'AS-Glob:TI-EVG:'+self._ACC+'TunesDelay-SP')
        self._timing_evg_tunesdelay_rb = _epics.PV(
            self._PREFIX_VACA+'AS-Glob:TI-EVG:'+self._ACC+'TunesDelay-RB',
            callback=self._callback_timing_state)

        self._timing_evg_tunesexttrig_cmd = _epics.PV(
            self._PREFIX_VACA+'AS-Glob:TI-EVG:'+self._ACC+'TunesExtTrig-Cmd')

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

        elif reason == 'ApplyDeltaKL-Cmd':
            done = self._apply_deltakl()
            if done:
                self._apply_deltakl_cmd_count += 1
                self.driver.setParam('ApplyDeltaKL-Cmd',
                                     self._apply_deltakl_cmd_count)
                self.driver.updatePVs()

        elif reason == 'CorrMat-SP':
            # Update local file
            done = save_corrparams(
                '/home/fac_files/lnls-sirius/machine-applications'
                '/as-ap-opticscorr/as_ap_opticscorr/tune/' +
                self._ACC.lower() + '-tunecorr.txt',
                value, len(self._QFAMS), self._qfam_nomkl)
            if done:
                self.driver.setParam('CorrMat-RB', value)

                # Update matrix used
                corrmat = value
                if self._ACC == 'SI':
                    corrmat = self._calc_matrix(corrmat)
                self._mat, _ = self._opticscorr.set_corr_mat(2, corrmat)
                self._calc_deltakl()
                self.driver.updatePVs()
                status = True

        elif reason == 'NominalKL-SP':
            # Update local file
            corrmat, _ = self._get_corrparams()
            done = save_corrparams(
                '/home/fac_files/lnls-sirius/machine-applications'
                '/as-ap-opticscorr/as_ap_opticscorr/tune/' +
                self._ACC.lower() + '-tunecorr.txt',
                corrmat, len(self._QFAMS), value)
            if done:
                self.driver.setParam('NominalKL-RB', value)

                # Update nomkl and matrix used according to the corr. method
                self._qfam_nomkl = value
                if self._ACC == 'SI':
                    corrmat = self._calc_matrix(corrmat)
                self._mat, _ = self._opticscorr.set_corr_mat(2, corrmat)
                self._calc_deltakl()
                self.driver.updatePVs()
                status = True

        elif reason == 'CorrMeth-Sel':
            if value != self._corr_method:
                self._corr_method = value
                self.driver.setParam('CorrMeth-Sts', self._corr_method)

                corrmat, _ = self._get_corrparams()
                if self._ACC == 'SI':
                    corrmat = self._calc_matrix(corrmat)
                self._mat, _ = self._opticscorr.set_corr_mat(2, corrmat)
                self._calc_deltakl()
                self.driver.updatePVs()
                status = True

        elif reason == 'CorrFactor-SP':
            self._corr_factor = value
            self.driver.setParam('CorrFactor-RB', value)
            self.driver.updatePVs()
            status = True

        elif reason == 'SyncCorr-Sel':
            if value != self._sync_corr:
                self._sync_corr = value
                for fam in self._QFAMS:
                    fam_index = self._QFAMS.index(fam)
                    self._qfam_check_opmode_sts[fam_index] = (
                        self._qfam_opmode_sts_pvs[fam].value)
                if any(op != self._sync_corr
                       for op in self._qfam_check_opmode_sts):
                    self._status = _siriuspy.util.update_integer_bit(
                        integer=self._status, number_of_bits=5, value=1, bit=2)
                else:
                    self._status = _siriuspy.util.update_integer_bit(
                        integer=self._status, number_of_bits=5, value=0, bit=2)
                self.driver.setParam('Status-Mon', self._status)
                self.driver.setParam('SyncCorr-Sts', self._sync_corr)
                self.driver.updatePVs()
                status = True

        elif reason == 'ConfigPS-Cmd':
            done = self._config_qfam_ps()
            if done:
                self._config_qfam_ps_cmd_count += 1
                self.driver.setParam('ConfigPS-Cmd',
                                     self._config_qfam_ps_cmd_count)
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

    def _get_corrparams(self):
        m, _ = read_corrparams(
            '/home/fac_files/lnls-sirius/machine-applications'
            '/as-ap-opticscorr/as_ap_opticscorr/tune/' +
            self._ACC.lower() + '-tunecorr.txt')

        tune_corrmat = len(self._QFAMS)*2*[0]
        index = 0
        for coordinate in [0, 1]:  # Read in C-like format
            for fam in range(len(self._QFAMS)):
                tune_corrmat[index] = float(m[coordinate][fam])
                index += 1

        nomkl = len(self._QFAMS)*[0]

        if self._ACC == 'SI':
            for fam in self._QFAMS:
                fam_index = self._QFAMS.index(fam)
                nomkl[fam_index] = float(m[2][fam_index])

        return tune_corrmat, nomkl

    def _calc_matrix(self, corrmat_svd):
        corrmat_svd = _np.array(corrmat_svd)
        corrmat_svd = _np.reshape(corrmat_svd, [2, len(self._QFAMS)])
        if self._corr_method == 0:
            corrmat_svd = corrmat_svd*_np.array(self._qfam_nomkl)

        corrmat_group = 4*[0]
        for col in [0, 1]:
            if col == 0:
                iterable = range(3)
            else:
                iterable = range(3, 8)
            for row in [0, 1]:
                if row == 0:
                    aux_index = 0
                else:
                    aux_index = 2
                for i in iterable:
                    corrmat_group[col+aux_index] += corrmat_svd.item((row, i))

        return corrmat_group

    def _calc_deltakl(self):
        if self._ACC == 'SI' and self._corr_method == 0:
            lastcalcd_grouppropfactor = self._opticscorr.calc_deltakl(
                self._delta_tunex, self._delta_tuney)
            for fam in self._QFAMS:
                fam_index = self._QFAMS.index(fam)
                if 'QF' in fam:
                    self._lastcalcd_deltakl[fam_index] = (
                        self._qfam_refkl[fam]*lastcalcd_grouppropfactor[0])
                elif 'QD' in fam:
                    self._lastcalcd_deltakl[fam_index] = (
                        self._qfam_refkl[fam]*lastcalcd_grouppropfactor[1])
        elif self._ACC == 'SI' and self._corr_method == 1:
            lastcalcd_groupdeltakl = self._opticscorr.calc_deltakl(
                self._delta_tunex, self._delta_tuney)
            for fam in self._QFAMS:
                fam_index = self._QFAMS.index(fam)
                if 'QF' in fam:
                    self._lastcalcd_deltakl[fam_index] = (
                        lastcalcd_groupdeltakl[0])
                elif 'QD' in fam:
                    self._lastcalcd_deltakl[fam_index] = (
                        lastcalcd_groupdeltakl[1])
        else:
            # if ACC=='BO'
            self._lastcalcd_deltakl = self._opticscorr.calc_deltakl(
                self._delta_tunex, self._delta_tuney)

        self.driver.setParam('Log-Mon', 'Calculated Delta KL')

        for fam in self._QFAMS:
            fam_index = self._QFAMS.index(fam)
            self.driver.setParam('LastCalcd' + fam + 'DeltaKL-Mon',
                                 self._lastcalcd_deltakl[fam_index])
        self.driver.updatePVs()

    def _apply_deltakl(self):
        if ((self._status == _ALLCLR_SYNCOFF and self._sync_corr == 0) or
                self._status == _ALLCLR_SYNCON):
            for fam in self._qfam_kl_sp_pvs:
                fam_index = self._QFAMS.index(fam)
                pv = self._qfam_kl_sp_pvs[fam]
                pv.put(self._qfam_refkl[fam] + (self._corr_factor/100) *
                       self._lastcalcd_deltakl[fam_index])
            self.driver.setParam('Log-Mon', 'Applied Delta KL')
            self.driver.updatePVs()

            if self._sync_corr == 1:
                self._timing_evg_tunesexttrig_cmd.put(0)
                self.driver.setParam('Log-Mon', 'Generated trigger')
                self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon', 'ERR:ApplyKL-Cmd failed')
            self.driver.updatePVs()
        return False

    def _update_ref(self):
        # updates reference
        for fam in self._QFAMS:
            self._qfam_refkl[fam] = self._qfam_kl_rb_pvs[fam].get()
            self.driver.setParam(fam + 'RefKL-Mon', self._qfam_refkl[fam])

            fam_index = self._QFAMS.index(fam)
            self._lastcalcd_deltakl[fam_index] = 0
            self.driver.setParam('LastCalcd' + fam + 'DeltaKL-Mon',
                                 self._lastcalcd_deltakl[fam_index])

        # the deltas from new kl references are zero
        self._delta_tunex = 0
        self._delta_tuney = 0
        self.driver.setParam('DeltaTuneX-SP', self._delta_tunex)
        self.driver.setParam('DeltaTuneY-SP', self._delta_tuney)
        delta_tunex, delta_tuney = self._estim_current_deltatune()
        self.driver.setParam('DeltaTuneX-RB', delta_tunex)
        self.driver.setParam('DeltaTuneY-RB', delta_tuney)

        self.driver.setParam('Log-Mon', 'Updated KL reference.')
        self.driver.updatePVs()

    def _estim_current_deltatune(self):
        qfam_deltakl = len(self._QFAMS)*[0]
        for fam in self._QFAMS:
            fam_index = self._QFAMS.index(fam)
            qfam_deltakl[fam_index] = (
                self._qfam_kl_rb[fam_index] - self._qfam_refkl[fam])
        corrmat, _ = self._get_corrparams()
        return self._opticscorr.estimate_current_deltatune(
            corrmat, qfam_deltakl)

    def _callback_init_refkl(self, pvname, value, cb_info, **kws):
        """Initialize RefKL-Mon pvs and remove this callback."""
        ps = pvname.split(self._PREFIX_VACA)[1]
        fam = ps.split(':')[1].split('-')[1]

        # Get reference
        self._qfam_refkl[fam] = value
        self.driver.setParam(fam + 'RefKL-Mon', self._qfam_refkl[fam])

        # Remove callback
        cb_info[1].remove_callback(cb_info[0])

    def _connection_callback_qfam_kl_rb(self, pvname, conn, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        if not conn:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' disconnected')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._QFAMS.index(fam)
        self._qfam_check_connection[fam_index] = (1 if conn else 0)

        # Change the first bit of correction status
        if any(q == 0 for q in self._qfam_check_connection):
            self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=1, bit=0)
        else:
            self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=0, bit=0)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_estimate_deltatune(self, pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._QFAMS.index(fam)
        self._qfam_kl_rb[fam_index] = value

        delta_tunex, delta_tuney = self._estim_current_deltatune()
        self.driver.setParam('DeltaTuneX-RB', delta_tunex)
        self.driver.setParam('DeltaTuneY-RB', delta_tuney)
        self.driver.updatePVs()

    def _callback_qfam_pwrstate_sts(self, pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        if value == 0:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Off')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._QFAMS.index(fam)
        self._qfam_check_pwrstate_sts[fam_index] = value

        # Change the second bit of correction status
        if any(q == 0 for q in self._qfam_check_pwrstate_sts):
            self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=1, bit=1)
        else:
            self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=0, bit=1)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_qfam_opmode_sts(self, pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        self.driver.setParam('Log-Mon', 'WARN:'+ps+' changed')
        self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._QFAMS.index(fam)
        self._qfam_check_opmode_sts[fam_index] = value

        # Change the third bit of correction status
        opmode = self._sync_corr
        if any(s != opmode for s in self._qfam_check_opmode_sts):
            self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=1, bit=2)
        else:
            self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=0, bit=2)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_qfam_ctrlmode_mon(self,  pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        if value == 1:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Local')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._QFAMS.index(fam)
        self._qfam_check_ctrlmode_mon[fam_index] = value

        # Change the fourth bit of correction status
        if any(q == 1 for q in self._qfam_check_ctrlmode_mon):
            self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=1, bit=3)
        else:
            self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=0, bit=3)
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
        if any(index == 0 for index in self._timing_check_config):
            self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=1, bit=4)
        else:
            self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=0, bit=4)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _config_qfam_ps(self):
        opmode = self._sync_corr
        for fam in self._QFAMS:
            if self._qfam_pwrstate_sel_pvs[fam].connected:
                self._qfam_pwrstate_sel_pvs[fam].put(1)
                self._qfam_opmode_sel_pvs[fam].put(opmode)
            else:
                self.driver.setParam('Log-Mon',
                                     'ERR:' + fam + ' is disconnected')
                self.driver.updatePVs()
                return False
        self.driver.setParam('Log-Mon', 'Sent configuration to quadrupoles')
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
            self.driver.setParam('Log-Mon', 'Sent configuration to timing')
            self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon', 'ERR:Some pv is disconnected')
            self.driver.updatePVs()
            return False
