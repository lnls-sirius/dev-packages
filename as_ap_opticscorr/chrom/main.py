"""Main module of AS-AP-ChromCorr IOC."""

import time as _time
import numpy as _np
import epics as _epics
import siriuspy as _siriuspy
from as_ap_opticscorr.opticscorr_utils import OpticsCorr
from as_ap_opticscorr.opticscorr_utils import read_corrparams, save_corrparams
import as_ap_opticscorr.chrom.pvs as _pvs

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

__version__ = _pvs._COMMIT_HASH


class App:
    """Main application for handling chromaticity correction."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _siriuspy.util.print_ioc_banner(
            ioc_name=_pvs._ACC+'-AP-ChromCorr',
            db=App.pvs_database,
            description=_pvs._ACC+'-AP-ChromCorr Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX)
        _siriuspy.util.save_ioc_pv_list(
            _pvs._ACC.lower()+'-ap-chromcorr',
            (_pvs._DEVICE,
             _pvs._PREFIX_VACA),
            App.pvs_database)

        self._driver = driver
        self._pvs_database = App.pvs_database

        self._status = 0x1f
        self._sfam_check_connection = len(_pvs._SFAMS)*[0]
        self._sfam_check_pwrstate_sts = len(_pvs._SFAMS)*[0]
        self._sfam_check_opmode_sts = len(_pvs._SFAMS)*[0]
        self._sfam_check_ctrlmode_mon = len(_pvs._SFAMS)*[0]

        self._apply_sl_cmd_count = 0
        self._config_sfam_ps_cmd_count = 0
        self._lastcalcd_sl = len(_pvs._SFAMS)*[0]

        self._sync_corr = 0
        self._sync_corr_cmd_count = 0
        self._config_timing_cmd_count = 0
        self._timing_check_config = 6*[0]

        # Initialize correction parameters from local file
        self._opticscorr = OpticsCorr()

        corrmat, nomchrom, nomsl = self._get_corrparams()
        self._sfam_slrefs = nomsl
        self.driver.setParam('NominalSL-SP', self._sfam_slrefs)
        self.driver.setParam('NominalSL-RB', self._sfam_slrefs)

        if _pvs._ACC.lower() == 'si':
            self._corr_method = 0
            corrmat = self._calc_prop_matrix(corrmat)
        else:
            self._corr_method = 1

        self._mat, invmat = self._opticscorr.set_corr_mat(
            'chrom', len(_pvs._SFAMS), corrmat)
        self.driver.setParam('CorrMat-SP', self._mat)
        self.driver.setParam('CorrMat-RB', self._mat)

        self._nomchrom = self._opticscorr.set_nomchrom(
            nomchrom[0], nomchrom[1])
        self.driver.setParam('NominalChrom-SP', self._nomchrom)
        self.driver.setParam('NominalChrom-RB', self._nomchrom)

        # Connect to Sextupoles Families
        self._sfam_sl_sp_pvs = {}
        self._sfam_sl_rb_pvs = {}
        self._sfam_pwrstate_sel_pvs = {}
        self._sfam_pwrstate_sts_pvs = {}
        self._sfam_opmode_sel_pvs = {}
        self._sfam_opmode_sts_pvs = {}
        self._sfam_ctrlmode_mon_pvs = {}

        for fam in _pvs._SFAMS:
            fam_index = _pvs._SFAMS.index(fam)
            self._sfam_sl_sp_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':SL-SP',
                connection_callback=self._connection_callback_sfam_sl_pvs)
            self._sfam_sl_sp_pvs[fam].wait_for_connection(timeout=0.05)
            self._sfam_sl_rb_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':SL-RB',
                connection_callback=self._connection_callback_sfam_sl_pvs)
            self._sfam_sl_rb_pvs[fam].wait_for_connection(timeout=0.05)
            self._sfam_check_connection[fam_index] = (
                self._sfam_sl_sp_pvs[fam].connected)

            self._sfam_pwrstate_sel_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':PwrState-Sel',
                connection_timeout=0.05)
            self._sfam_pwrstate_sts_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':PwrState-Sts',
                connection_timeout=0.05)

            self._sfam_opmode_sel_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':OpMode-Sel',
                connection_timeout=0.05)
            self._sfam_opmode_sts_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':OpMode-Sts',
                connection_timeout=0.05)

            self._sfam_ctrlmode_mon_pvs[fam] = _epics.PV(
                _pvs._PREFIX_VACA+_pvs._ACC+'-Fam:MA-'+fam+':CtrlMode-Mon',
                connection_timeout=0.05)

        for fam in _pvs._SFAMS:
            fam_index = _pvs._SFAMS.index(fam)
            self._sfam_sl_rb_pvs[fam].add_callback(self._callback_sfam_sl_rb)

            self._sfam_pwrstate_sts_pvs[fam].add_callback(
                self._callback_sfam_pwrstate_sts)
            self._sfam_check_pwrstate_sts[fam_index] = (
                self._sfam_pwrstate_sts_pvs[fam].value)

            self._sfam_opmode_sts_pvs[fam].add_callback(
                self._callback_sfam_opmode_sts)
            self._sfam_check_opmode_sts[fam_index] = (
                self._sfam_opmode_sts_pvs[fam].value)

            self._sfam_ctrlmode_mon_pvs[fam].add_callback(
                self._callback_sfam_ctrlmode_mon)
            self._sfam_check_ctrlmode_mon[fam_index] = (
                self._sfam_ctrlmode_mon_pvs[fam].value)

        # Initialize chromaticity values
        self._chromx_sp, self._chromy_sp = self._estim_current_chrom('sp')
        self.driver.setParam('ChromX-SP', self._chromx_sp)
        self.driver.setParam('ChromY-SP', self._chromy_sp)

        self._chromx_rb, self._chromy_rb = self._estim_current_chrom('rb')
        self.driver.setParam('ChromX-RB', self._chromx_rb)
        self.driver.setParam('ChromY-RB', self._chromy_rb)

        # Connect to Timing
        self._timing_sexts_state_sel = _epics.PV(
            _pvs._PREFIX_VACA+_pvs._ACC+'-Glob:TI-Sexts:State-Sel',
            connection_timeout=0.05)
        self._timing_sexts_state_sts = _epics.PV(
            _pvs._PREFIX_VACA+_pvs._ACC+'-Glob:TI-Sexts:State-Sts',
            connection_timeout=0.05)
        self._timing_sexts_state_sts.add_callback(self._callback_timing_state)

        self._timing_sexts_evgparam_sel = _epics.PV(
            _pvs._PREFIX_VACA+_pvs._ACC+'-Glob:TI-Sexts:EVGParam-Sel',
            connection_timeout=0.05)
        self._timing_sexts_evgparam_sts = _epics.PV(
            _pvs._PREFIX_VACA+_pvs._ACC+'-Glob:TI-Sexts:EVGParam-Sts',
            connection_timeout=0.05)
        self._timing_sexts_evgparam_sts.add_callback(
            self._callback_timing_state)

        self._timing_sexts_pulses_sp = _epics.PV(
            _pvs._PREFIX_VACA+_pvs._ACC+'-Glob:TI-Sexts:Pulses-SP',
            connection_timeout=0.05)
        self._timing_sexts_pulses_rb = _epics.PV(
            _pvs._PREFIX_VACA+_pvs._ACC+'-Glob:TI-Sexts:Pulses-RB',
            connection_timeout=0.05)
        self._timing_sexts_pulses_rb.add_callback(self._callback_timing_state)

        self._timing_sexts_duration_sp = _epics.PV(
            _pvs._PREFIX_VACA+_pvs._ACC+'-Glob:TI-Sexts:Duration-SP',
            connection_timeout=0.05)
        self._timing_sexts_duration_rb = _epics.PV(
            _pvs._PREFIX_VACA+_pvs._ACC+'-Glob:TI-Sexts:Duration-RB',
            connection_timeout=0.05)
        self._timing_sexts_duration_rb.add_callback(
            self._callback_timing_state)

        self._timing_evg_chrommode_sel = _epics.PV(
            _pvs._PREFIX_VACA+'AS-Glob:TI-EVG:'+_pvs._ACC+'ChromsMode-Sel',
            connection_timeout=0.05)
        self._timing_evg_chrommode_sts = _epics.PV(
            _pvs._PREFIX_VACA+'AS-Glob:TI-EVG:'+_pvs._ACC+'ChromsMode-Sts',
            connection_timeout=0.05)
        self._timing_evg_chrommode_sts.add_callback(
            self._callback_timing_state)

        self._timing_evg_chromdelay_sp = _epics.PV(
            _pvs._PREFIX_VACA+'AS-Glob:TI-EVG:'+_pvs._ACC+'ChromsDelay-SP',
            connection_timeout=0.05)
        self._timing_evg_chromdelay_rb = _epics.PV(
            _pvs._PREFIX_VACA+'AS-Glob:TI-EVG:'+_pvs._ACC+'ChromsDelay-RB',
            connection_timeout=0.05)
        self._timing_evg_chromdelay_rb.add_callback(
            self._callback_timing_state)

        self._timing_evg_chromexttrig_cmd = _epics.PV(
            _pvs._PREFIX_VACA+'AS-Glob:TI-EVG:'+_pvs._ACC+'ChromsExtTrig-Cmd',
            connection_timeout=0.05)

        # Set current status
        if all(conn == 1 for conn in self._sfam_check_connection):
            self._status = self._status & 0x1e
        if all(pwr == 1 for pwr in self._sfam_check_pwrstate_sts):
            self._status = self._status & 0x1d
        if all(op == self._sync_corr for op in self._sfam_check_opmode_sts):
            self._status = self._status & 0x1b
        if all(ctrl == 0 for ctrl in self._sfam_check_ctrlmode_mon):
            self._status = self._status & 0x17
        if all(conf == 1 for conf in self._timing_check_config):
            self._status = self._status & 0x0f
        self.driver.setParam('Status-Mon', self._status)

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
        if reason == 'ChromX-SP':
            self._chromx_sp = value
            self._calc_sl()
            self.driver.updatePVs()
            status = True

        elif reason == 'ChromY-SP':
            self._chromy_sp = value
            self._calc_sl()
            self.driver.updatePVs()
            status = True

        elif reason == 'ApplySL-Cmd':
            status = self._apply_sl()
            if status:
                self._apply_sl_cmd_count += 1
                self.driver.setParam('ApplySL-Cmd', self._apply_sl_cmd_count)
                self.driver.updatePVs()

        elif reason == 'CorrMat-SP':
            # Update local file
            save_corrparams(
                '/home/fac_files/lnls-sirius/machine-applications'
                '/as-ap-opticscorr/as_ap_opticscorr/chrom/' +
                _pvs._ACC.lower() + '-chromcorr.txt',
                value, len(_pvs._SFAMS), self._nomchrom, self._sfam_slrefs)
            self.driver.setParam('CorrMat-RB', value)

            # Update matrix used
            corrmat = value
            if self._corr_method == 0:
                corrmat = self._calc_prop_matrix(corrmat)
            self._mat, invmat = self._opticscorr.set_corr_mat(
                'chrom', len(_pvs._SFAMS), corrmat)
            self._calc_sl()
            self.driver.updatePVs()
            status = True

        elif reason == 'NominalChrom-SP':
            # Update local file
            corrmat, _, _ = self._get_corrparams()
            save_corrparams(
                '/home/fac_files/lnls-sirius/machine-applications'
                '/as-ap-opticscorr/as_ap_opticscorr/chrom/' +
                _pvs._ACC.lower() + '-chromcorr.txt',
                corrmat, len(_pvs._SFAMS), value, self._sfam_slrefs)
            self.driver.setParam('NominalChrom-RB', value)
            self.driver.updatePVs()

            # Update nomchrom used
            self._nomchrom = self._opticscorr.set_nomchrom(
                value[0], value[1])
            self._calc_sl()
            self.driver.updatePVs()
            status = True

        elif reason == 'NominalSL-SP':
            corrmat, _, _ = self._get_corrparams()
            # Update local file
            save_corrparams(
                '/home/fac_files/lnls-sirius/machine-applications'
                '/as-ap-opticscorr/as_ap_opticscorr/chrom/' +
                _pvs._ACC.lower() + '-chromcorr.txt',
                corrmat, len(_pvs._SFAMS), self._nomchrom, value)
            self.driver.setParam('NominalSL-RB', value)
            self.driver.updatePVs()

            # Update nomsl and matrix used according to the corr. method
            self._sfam_slrefs = value
            if self._corr_method == 0:
                corrmat, _, _ = self._get_corrparams()
                corrmat = self._calc_prop_matrix(corrmat)
                self._mat, invmat = self._opticscorr.set_corr_mat(
                    'chrom', len(_pvs._SFAMS), corrmat)
            self._calc_sl()
            self.driver.updatePVs()
            status = True

        elif reason == 'CorrMeth-Sel':
            if value != self._corr_method:
                self._corr_method = value
                self.driver.setParam('CorrMeth-Sts', self._corr_method)

                corrmat, _, _ = self._get_corrparams()
                if value == 0:
                    corrmat = self._calc_prop_matrix(corrmat)
                self._mat, invmat = self._opticscorr.set_corr_mat(
                    'chrom', len(_pvs._SFAMS), corrmat)
                self._calc_sl()
                self.driver.updatePVs()
                status = True

        elif reason == 'SyncCorr-Sel':
            if value != self._sync_corr:
                self._sync_corr = value
                self.driver.setParam('SyncCorr-Sts', self._sync_corr)
                self.driver.updatePVs()
                status = True

        elif reason == 'ConfigPS-Cmd':
            status = self._config_sfam_ps()
            if status:
                self._config_sfam_ps_cmd_count += 1
                self.driver.setParam('ConfigPS-Cmd',
                                     self._config_sfam_ps_cmd_count)
                self.driver.updatePVs()

        elif reason == 'ConfigTiming-Cmd':
            status = self._config_timing()
            if status:
                self._config_timing_cmd_count += 1
                self.driver.setParam('ConfigTiming-Cmd',
                                     self._config_timing_cmd_count)
                self.driver.updatePVs()

        return status  # return True to invoke super().write of PCASDriver

    def _get_corrparams(self):
        m, _ = read_corrparams(
            '/home/fac_files/lnls-sirius/machine-applications'
            '/as-ap-opticscorr/as_ap_opticscorr/chrom/' +
            _pvs._ACC.lower() + '-chromcorr.txt')

        nomchrom = [0, 0]
        nomchrom[0] = float(m[0][0])
        nomchrom[1] = float(m[0][1])

        chrom_corrmat = len(_pvs._SFAMS)*2*[0]
        index = 0
        for coordinate in [1, 2]:  # Read in C-like format
            for fam in range(len(_pvs._SFAMS)):
                chrom_corrmat[index] = float(m[coordinate][fam])
                index += 1

        nomsl = len(_pvs._SFAMS)*[0]
        for fam in _pvs._SFAMS:
            fam_index = _pvs._SFAMS.index(fam)
            nomsl[fam_index] = float(m[3][fam_index])
        return chrom_corrmat, nomchrom, nomsl

    def _calc_sl(self):
        if _pvs._ACC == 'SI' and self._corr_method == 0:
            lastcalcd_propfactor = self._opticscorr.calc_deltasl(
                self._chromx_sp, self._chromy_sp)
            for fam in _pvs._SFAMS:
                fam_index = _pvs._SFAMS.index(fam)
                self._lastcalcd_sl[fam_index] = (
                    self._sfam_slrefs[fam_index] *
                    (1+lastcalcd_propfactor[fam_index]))
        else:
            # if ACC=='BO' or (ACC=='SI' and corr_method==1)
            lastcalcd_deltasl = self._opticscorr.calc_deltasl(
                self._chromx_sp, self._chromy_sp)
            for fam in _pvs._SFAMS:
                fam_index = _pvs._SFAMS.index(fam)
                self._lastcalcd_sl[fam_index] = (
                    self._sfam_slrefs[fam_index] +
                    lastcalcd_deltasl[fam_index])

        self.driver.setParam('Log-Mon', 'Calculated SL')

        for fam in _pvs._SFAMS:
            fam_index = _pvs._SFAMS.index(fam)
            self.driver.setParam('LastCalcd' + fam + 'SL-Mon',
                                 self._lastcalcd_sl[fam_index])
        self.driver.updatePVs()

    def _apply_sl(self):
        pvs = self._sfam_sl_sp_pvs
        if ((self._status == 0x00 and self._sync_corr == 1) or
                (self._status == 0x10 and self._sync_corr == 0)):
            for fam in pvs:
                fam_index = _pvs._SFAMS.index(fam)
                pv = pvs[fam]
                pv.put(self._lastcalcd_sl[fam_index])
            self.driver.setParam('Log-Mon', 'Applied SL')
            self.driver.updatePVs()

            if self._sync_corr == 1:
                self._timing_evg_chromexttrig_cmd.put(0)
                self.driver.setParam('Log-Mon', 'Generated trigger')
                self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon', 'ERR:ApplySL-Cmd failed')
            self.driver.updatePVs()
        return False

    def _estim_current_chrom(self, pv_type):
        if pv_type == 'sp':
            pvs = self._sfam_sl_sp_pvs
        elif pv_type == 'rb':
            pvs = self._sfam_sl_rb_pvs

        sfam_sl = len(_pvs._SFAMS)*[0]
        sfam_deltasl = len(_pvs._SFAMS)*[0]
        if ((not any(s == 0 for s in self._sfam_check_connection)) and
                (not any(s == 0 for s in self._sfam_check_pwrstate_sts))):
            for fam in _pvs._SFAMS:
                fam_index = _pvs._SFAMS.index(fam)
                pv = pvs[fam]
                sfam_sl[fam_index] = pv.get()
                sfam_deltasl[fam_index] = (
                    sfam_sl[fam_index]-self._sfam_slrefs[fam_index])
                if self._corr_method == 0:
                    sfam_deltasl[fam_index] = (
                        sfam_deltasl[fam_index]/self._sfam_slrefs[fam_index])
            return self._opticscorr.estimate_current_chrom(sfam_deltasl)
        else:
            return [0, 0]

    def _calc_prop_matrix(self, corrmat):
        corrmat = _np.array(corrmat)
        corrmat = _np.reshape(corrmat, [2, len(_pvs._SFAMS)])
        corrmat = corrmat*_np.array(self._sfam_slrefs)
        corrmat = list(corrmat.flatten())
        return corrmat

    def _connection_callback_sfam_sl_pvs(self, pvname, conn, **kws):
        ps = pvname.split(_pvs._PREFIX_VACA)[1]
        if not conn:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' disconnected')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = _pvs._SFAMS.index(fam)
        self._sfam_check_connection[fam_index] = (1 if conn else 0)

        # Change the first bit of correction status
        if any(s == 0 for s in self._sfam_check_connection):
            conn_status = 0x01
            self._status = self._status | conn_status
        else:
            conn_status = 0x1e
            self._status = self._status & conn_status
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_sfam_sl_rb(self, **kws):
        self._chromx_rb, self._chromy_rb = self._estim_current_chrom('rb')
        self.driver.setParam('ChromX-RB', self._chromx_rb)
        self.driver.setParam('ChromY-RB', self._chromy_rb)
        self.driver.updatePVs()

    def _callback_sfam_pwrstate_sts(self, pvname, value, **kws):
        ps = pvname.split(_pvs._PREFIX_VACA)[1]
        if value == 0:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Off')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = _pvs._SFAMS.index(fam)
        self._sfam_check_pwrstate_sts[fam_index] = value

        # Change the second bit of correction status
        if any(s == 0 for s in self._sfam_check_pwrstate_sts):
            conn_status = 0x02
            self._status = self._status | conn_status
        else:
            conn_status = 0x1d
            self._status = self._status & conn_status
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_sfam_opmode_sts(self, pvname, value, **kws):
        ps = pvname.split(_pvs._PREFIX_VACA)[1]
        self.driver.setParam('Log-Mon', 'WARN:'+ps+' changed')
        self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = _pvs._SFAMS.index(fam)
        self._sfam_check_opmode_sts[fam_index] = value

        # Change the third bit of correction status
        opmode = self._sync_corr
        if any(s != opmode for s in self._sfam_check_opmode_sts):
            conn_status = 0x04
            self._status = self._status | conn_status
        else:
            conn_status = 0x1b
            self._status = self._status & conn_status
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_sfam_ctrlmode_mon(self,  pvname, value, **kws):
        ps = pvname.split(_pvs._PREFIX_VACA)[1]
        if value == 1:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Local')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = _pvs._SFAMS.index(fam)
        self._sfam_check_ctrlmode_mon[fam_index] = value

        # Change the fourth bit of correction status
        if any(s == 1 for s in self._sfam_check_ctrlmode_mon):
            conn_status = 0x08
            self._status = self._status | conn_status
        else:
            conn_status = 0x17
            self._status = self._status & conn_status
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_timing_state(self, pvname, value, **kws):
        if 'Sexts:State' in pvname:
            self._timing_check_config[0] = value  # Enbl
        elif 'Sexts:EVGParam' in pvname:
            self._timing_check_config[1] = (1 if value == 1 else 0)  # Chroms
        elif 'Sexts:Pulses' in pvname:
            self._timing_check_config[2] = (1 if value == 1 else 0)  # 1 pulse
        elif 'Sexts:Duration' in pvname:
            self._timing_check_config[3] = (1 if value == 0.15 else 0)  # 150us
        elif 'ChromsMode' in pvname:
            self._timing_check_config[4] = (1 if value == 3 else 0)  # External
        elif 'ChromsDelay' in pvname:
            self._timing_check_config[5] = (1 if value == 0 else 0)  # 0s

        # Change the fifth bit of correction status
        if any(index == 0 for index in self._timing_check_config):
            conn_status = 0x10
            self._status = self._status | conn_status
        else:
            conn_status = 0x0f
            self._status = self._status & conn_status
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _config_sfam_ps(self):
        opmode = self._sync_corr
        for fam in _pvs._SFAMS:
            if self._sfam_pwrstate_sel_pvs[fam].connected:
                self._sfam_pwrstate_sel_pvs[fam].put(1)
                self._sfam_opmode_sel_pvs[fam].put(opmode)
            else:
                self.driver.setParam('Log-Mon',
                                     'ERR:' + fam + ' is disconnected')
                self.driver.updatePVs()
                return False
        self.driver.setParam('Log-Mon', 'Sent configuration to sextupoles')
        self.driver.updatePVs()
        return True

    def _config_timing(self):
        self._timing_sexts_state_sel.put(1)
        self._timing_sexts_evgparam_sel.put(1)
        self._timing_sexts_pulses_sp.put(1)
        self._timing_sexts_duration_sp.put(0.15)
        self._timing_evg_chrommode_sel.put(3)
        self._timing_evg_chromdelay_sp.put(0)
        _time.sleep(0.05)
        if any(index == 0 for index in self._timing_check_config):
            self.driver.setParam('Log-Mon',
                                 'ERR:Timing configuration failed')
            self.driver.updatePVs()
            return False
        else:
            self.driver.setParam('Log-Mon',
                                 'Configurated timing')
            self.driver.updatePVs()
            return True
