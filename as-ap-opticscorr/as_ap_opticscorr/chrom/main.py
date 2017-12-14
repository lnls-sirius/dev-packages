"""Main module of AS-AP-ChromCorr IOC."""

import time as _time
import numpy as _np
import epics as _epics
import siriuspy as _siriuspy
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from as_ap_opticscorr.opticscorr_utils import OpticsCorr
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


# Constants
_ALLSET = 0x1f
_ALLCLR_SYNCON = 0x00
_ALLCLR_SYNCOFF = 0x10


class App:
    """Main application for handling chromaticity correction."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _pvs.print_banner_and_save_pv_list()
        self._SFAMS = _pvs.get_corr_fams()
        self._ACC = _pvs.get_pvs_section()
        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()

        self._driver = driver

        self._chromx = 0
        self._chromy = 0

        self._status = _ALLSET
        self._sfam_check_connection = len(self._SFAMS)*[0]
        self._sfam_check_pwrstate_sts = len(self._SFAMS)*[0]
        self._sfam_check_opmode_sts = len(self._SFAMS)*[-1]
        self._sfam_check_ctrlmode_mon = len(self._SFAMS)*[1]

        self._apply_sl_cmd_count = 0
        self._config_sfam_ps_cmd_count = 0
        self._lastcalcd_sl = len(self._SFAMS)*[0]

        self._sfam_sl_rb = len(self._SFAMS)*[0]

        self._sync_corr = 0
        self._sync_corr_cmd_count = 0
        self._config_timing_cmd_count = 0
        self._timing_check_config = 6*[0]

        # Initialize correction parameters from local file
        self._opticscorr = OpticsCorr()

        if self._ACC.lower() == 'si':
            self._corr_method = 0
        else:
            self._corr_method = 1

        config_name = self._get_config_name()
        self._get_corrparams(config_name)
        self.driver.setParam('CorrParamsConfigName-SP', config_name)
        self.driver.setParam('CorrParamsConfigName-RB', config_name)
        self.driver.setParam('CorrMat-Mon', self._corrmat_add_svd)
        self.driver.setParam('NominalSL-Mon', self._sfam_nomsl)
        self.driver.setParam('NominalChrom-Mon', self._nomchrom)

        # Connect to Sextupoles Families
        self._sfam_sl_sp_pvs = {}
        self._sfam_sl_rb_pvs = {}
        self._sfam_pwrstate_sel_pvs = {}
        self._sfam_pwrstate_sts_pvs = {}
        self._sfam_opmode_sel_pvs = {}
        self._sfam_opmode_sts_pvs = {}
        self._sfam_ctrlmode_mon_pvs = {}

        for fam in self._SFAMS:
            self._sfam_sl_sp_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':SL-SP')

            self._sfam_sl_rb_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':SL-RB',
                callback=self._callback_estimate_chrom,
                connection_callback=self._connection_callback_sfam_sl_rb)

            self._sfam_pwrstate_sel_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':PwrState-Sel')
            self._sfam_pwrstate_sts_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':PwrState-Sts',
                callback=self._callback_sfam_pwrstate_sts)

            self._sfam_opmode_sel_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':OpMode-Sel')
            self._sfam_opmode_sts_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':OpMode-Sts',
                callback=self._callback_sfam_opmode_sts)

            self._sfam_ctrlmode_mon_pvs[fam] = _epics.PV(
                self._PREFIX_VACA+self._ACC+'-Fam:MA-'+fam+':CtrlMode-Mon',
                callback=self._callback_sfam_ctrlmode_mon)

        # Connect to Timing
        self._timing_sexts_state_sel = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Sexts:State-Sel')
        self._timing_sexts_state_sts = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Sexts:State-Sts',
            callback=self._callback_timing_state)

        self._timing_sexts_evgparam_sel = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Sexts:EVGParam-Sel')
        self._timing_sexts_evgparam_sts = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Sexts:EVGParam-Sts',
            callback=self._callback_timing_state)

        self._timing_sexts_pulses_sp = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Sexts:Pulses-SP')
        self._timing_sexts_pulses_rb = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Sexts:Pulses-RB',
            callback=self._callback_timing_state)

        self._timing_sexts_duration_sp = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Sexts:Duration-SP')
        self._timing_sexts_duration_rb = _epics.PV(
            self._PREFIX_VACA+self._ACC+'-Glob:TI-Sexts:Duration-RB',
            callback=self._callback_timing_state)

        self._timing_evg_chromsmode_sel = _epics.PV(
            self._PREFIX_VACA+'AS-Glob:TI-EVG:'+self._ACC+'ChromsMode-Sel')
        self._timing_evg_chromsmode_sts = _epics.PV(
            self._PREFIX_VACA+'AS-Glob:TI-EVG:'+self._ACC+'ChromsMode-Sts',
            callback=self._callback_timing_state)

        self._timing_evg_chromsdelay_sp = _epics.PV(
            self._PREFIX_VACA+'AS-Glob:TI-EVG:'+self._ACC+'ChromsDelay-SP')
        self._timing_evg_chromsdelay_rb = _epics.PV(
            self._PREFIX_VACA+'AS-Glob:TI-EVG:'+self._ACC+'ChromsDelay-RB',
            callback=self._callback_timing_state)

        self._timing_evg_chromsexttrig_cmd = _epics.PV(
            self._PREFIX_VACA+'AS-Glob:TI-EVG:'+self._ACC+'ChromsExtTrig-Cmd')

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
            self._chromx = value
            self._calc_sl()
            self.driver.updatePVs()
            status = True

        elif reason == 'ChromY-SP':
            self._chromy = value
            self._calc_sl()
            self.driver.updatePVs()
            status = True

        elif reason == 'ApplySL-Cmd':
            done = self._apply_sl()
            if done:
                self._apply_sl_cmd_count += 1
                self.driver.setParam('ApplySL-Cmd', self._apply_sl_cmd_count)
                self.driver.updatePVs()

        elif reason == 'CorrParamsConfigName-SP':
            done = self._get_corrparams(value)
            if done:
                self._set_config_name(value)
                self._calc_sl()
                self.driver.setParam('CorrParamsConfigName-RB', value)
                self.driver.setParam('CorrMat-Mon', self._corrmat_add_svd)
                self.driver.setParam('NominalChrom-Mon', self._nomchrom)
                self.driver.setParam('NominalSL-Mon', self._sfam_nomsl)
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
                self.driver.setParam('CorrMeth-Sts', self._corr_method)

                corrmat, _, _ = self._get_corrparams()
                if value == 0:
                    corrmat = self._calc_prop_matrix(corrmat)
                self._mat, _ = self._opticscorr.set_corr_mat(
                    len(self._SFAMS), corrmat)
                self._calc_sl()
                self.driver.updatePVs()
                status = True

        elif reason == 'SyncCorr-Sel':
            if value != self._sync_corr:
                self._sync_corr = value
                for fam in self._SFAMS:
                    fam_index = self._SFAMS.index(fam)
                    self._sfam_check_opmode_sts[fam_index] = (
                        self._sfam_opmode_sts_pvs[fam].value)
                if any(op != self._sync_corr
                       for op in self._sfam_check_opmode_sts):
                    self._status = self._status = \
                        _siriuspy.util.update_integer_bit(
                            integer=self._status, number_of_bits=5,
                            value=1, bit=2)
                else:
                    self._status = self._status = \
                        _siriuspy.util.update_integer_bit(
                            integer=self._status, number_of_bits=5,
                            value=0, bit=2)
                self.driver.setParam('Status-Mon', self._status)
                self.driver.setParam('SyncCorr-Sts', self._sync_corr)
                self.driver.updatePVs()
                status = True

        elif reason == 'ConfigPS-Cmd':
            done = self._config_sfam_ps()
            if done:
                self._config_sfam_ps_cmd_count += 1
                self.driver.setParam('ConfigPS-Cmd',
                                     self._config_sfam_ps_cmd_count)
                self.driver.updatePVs()

        elif reason == 'ConfigTiming-Cmd':
            done = self._config_timing()
            if done:
                self._config_timing_cmd_count += 1
                self.driver.setParam('ConfigTiming-Cmd',
                                     self._config_timing_cmd_count)
                self.driver.updatePVs()

        return status  # return True to invoke super().write of PCASDriver

    def _get_corrparams(self, config_name):
        """Get response matrix from configurations database."""
        cs = _ConfigService()
        q = cs.get_config(self._ACC.lower()+'_chromcorr_params', config_name)
        done = q['code']

        if done == 200:
            done = True
            params = q['result']['value']

            self._corrmat_add_svd = [item for sublist in params['matrix']
                                     for item in sublist]
            self._sfam_nomsl = params['nominal SLs']

            if self._corr_method == 0:
                corrmat = self._calc_prop_matrix(self._corrmat_add_svd)
            else:
                corrmat = self._corrmat_add_svd
            self._mat, _ = self._opticscorr.set_corr_mat(
                len(self._SFAMS), corrmat)

            nomchrom = params['nominal chrom']
            self._nomchrom = self._opticscorr.set_nomchrom(
                             nomchrom[0], nomchrom[1])
        else:
            done = False
        return done

    def _get_config_name(self):
        f = open('/home/fac_files/lnls-sirius/machine-applications'
                 '/as-ap-opticscorr/as_ap_opticscorr/chrom/' +
                 self._ACC.lower() + '-chromcorr.txt', 'r')
        config_name = f.read().strip('\n')
        f.close()
        return config_name

    def _set_config_name(self, config_name):
        f = open('/home/fac_files/lnls-sirius/machine-applications'
                 '/as-ap-opticscorr/as_ap_opticscorr/chrom/' +
                 self._ACC.lower() + '-chromcorr.txt', 'w')
        f.write(config_name)
        f.close()

    def _calc_prop_matrix(self, corrmat):
        corrmat = _np.array(corrmat)
        corrmat = _np.reshape(corrmat, [2, len(self._SFAMS)])
        corrmat = corrmat*_np.array(self._sfam_nomsl)
        corrmat = list(corrmat.flatten())
        return corrmat

    def _calc_sl(self):
        if self._ACC == 'SI' and self._corr_method == 0:
            lastcalcd_propfactor = self._opticscorr.calc_deltasl(
                self._chromx, self._chromy)
            for fam in self._SFAMS:
                fam_index = self._SFAMS.index(fam)
                self._lastcalcd_sl[fam_index] = (
                    self._sfam_nomsl[fam_index] *
                    (1+lastcalcd_propfactor[fam_index]))
        else:
            # if ACC=='BO' or (ACC=='SI' and corr_method==1)
            lastcalcd_deltasl = self._opticscorr.calc_deltasl(
                self._chromx, self._chromy)
            for fam in self._SFAMS:
                fam_index = self._SFAMS.index(fam)
                self._lastcalcd_sl[fam_index] = (
                    self._sfam_nomsl[fam_index] +
                    lastcalcd_deltasl[fam_index])

        self.driver.setParam('Log-Mon', 'Calculated SL')

        for fam in self._SFAMS:
            fam_index = self._SFAMS.index(fam)
            self.driver.setParam('LastCalcd' + fam + 'SL-Mon',
                                 self._lastcalcd_sl[fam_index])
        self.driver.updatePVs()

    def _apply_sl(self):
        if ((self._status == _ALLCLR_SYNCON and self._sync_corr == 1) or
                ((self._status == _ALLCLR_SYNCOFF or
                  self._status == _ALLCLR_SYNCON) and self._sync_corr == 0)):
            pvs = self._sfam_sl_sp_pvs
            for fam in pvs:
                fam_index = self._SFAMS.index(fam)
                pv = pvs[fam]
                pv.put(self._lastcalcd_sl[fam_index])
            self.driver.setParam('Log-Mon', 'Applied SL')
            self.driver.updatePVs()

            if self._sync_corr == 1:
                self._timing_evg_chromsexttrig_cmd.put(0)
                self.driver.setParam('Log-Mon', 'Generated trigger')
                self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon', 'ERR:ApplySL-Cmd failed')
            self.driver.updatePVs()
        return False

    def _estimate_current_chrom(self):
        sfam_deltasl = len(self._SFAMS)*[0]
        for fam in self._SFAMS:
            fam_index = self._SFAMS.index(fam)
            sfam_deltasl[fam_index] = (
                self._sfam_sl_rb[fam_index] - self._sfam_nomsl[fam_index])
            if self._corr_method == 0:
                sfam_deltasl[fam_index] = (sfam_deltasl[fam_index] /
                                           self._sfam_nomsl[fam_index])
        return self._opticscorr.estimate_current_chrom(sfam_deltasl)

    def _connection_callback_sfam_sl_rb(self, pvname, conn, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        if not conn:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' disconnected')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._SFAMS.index(fam)
        self._sfam_check_connection[fam_index] = (1 if conn else 0)

        # Change the first bit of correction status
        if any(s == 0 for s in self._sfam_check_connection):
            self._status = self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=1, bit=0)
        else:
            self._status = self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=0, bit=0)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_estimate_chrom(self, pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._SFAMS.index(fam)
        self._sfam_sl_rb[fam_index] = value

        chromx_rb, chromy_rb = self._estimate_current_chrom()
        self.driver.setParam('ChromX-RB', chromx_rb)
        self.driver.setParam('ChromY-RB', chromy_rb)
        self.driver.updatePVs()

    def _callback_sfam_pwrstate_sts(self, pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        if value == 0:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Off')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._SFAMS.index(fam)
        self._sfam_check_pwrstate_sts[fam_index] = value

        # Change the second bit of correction status
        if any(s == 0 for s in self._sfam_check_pwrstate_sts):
            self._status = self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=1, bit=1)
        else:
            self._status = self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=0, bit=1)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_sfam_opmode_sts(self, pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        self.driver.setParam('Log-Mon', 'WARN:'+ps+' changed')
        self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._SFAMS.index(fam)
        self._sfam_check_opmode_sts[fam_index] = value

        # Change the third bit of correction status
        opmode = self._sync_corr
        if any(s != opmode for s in self._sfam_check_opmode_sts):
            self._status = self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=1, bit=2)
        else:
            self._status = self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=0, bit=2)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _callback_sfam_ctrlmode_mon(self,  pvname, value, **kws):
        ps = pvname.split(self._PREFIX_VACA)[1]
        if value == 1:
            self.driver.setParam('Log-Mon', 'WARN:'+ps+' is Local')
            self.driver.updatePVs()

        fam = ps.split(':')[1].split('-')[1]
        fam_index = self._SFAMS.index(fam)
        self._sfam_check_ctrlmode_mon[fam_index] = value

        # Change the fourth bit of correction status
        if any(s == 1 for s in self._sfam_check_ctrlmode_mon):
            self._status = self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=1, bit=3)
        else:
            self._status = self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=0, bit=3)
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
            self._status = self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=1, bit=4)
        else:
            self._status = self._status = _siriuspy.util.update_integer_bit(
                integer=self._status, number_of_bits=5, value=0, bit=4)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePVs()

    def _config_sfam_ps(self):
        opmode = self._sync_corr
        for fam in self._SFAMS:
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
        if not any(pv.connected is False for pv in [
                self._timing_sexts_state_sel,
                self._timing_sexts_evgparam_sel,
                self._timing_sexts_pulses_sp,
                self._timing_sexts_duration_sp,
                self._timing_evg_chromsmode_sel,
                self._timing_evg_chromsdelay_sp]):
            self._timing_sexts_state_sel.put(1)
            self._timing_sexts_evgparam_sel.put(1)
            self._timing_sexts_pulses_sp.put(1)
            self._timing_sexts_duration_sp.put(0.15)
            self._timing_evg_chromsmode_sel.put(3)
            self._timing_evg_chromsdelay_sp.put(0)
            self.driver.setParam('Log-Mon', 'Sent configuration to timing')
            self.driver.updatePVs()
            return True
        else:
            self.driver.setParam('Log-Mon', 'ERR:Some pv is disconnected')
            self.driver.updatePVs()
            return False
