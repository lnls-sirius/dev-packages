"""Main module of AS-AP-ChromCorr IOC."""

import time as _time
from epics import PV as _PV

from siriuspy import util as _util
from siriuspy.callbacks import Callback as _Callback
from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.search import LLTimeSearch as _LLTimeSearch
from siriuspy.clientconfigdb import ConfigDBClient as _ConfigDBClient, \
    ConfigDBException as _ConfigDBException
from siriuspy.pwrsupply.csdev import Const as _PSConst
from siriuspy.timesys.csdev import Const as _TIConst, \
    get_hl_trigger_database as _get_trig_db

from siriuspy.optics.opticscorr import OpticsCorr as _OpticsCorr
from siriuspy.opticscorr.csdev import Const as _Const, \
    get_chrom_database as _get_database
from siriuspy.opticscorr.utils import \
    get_config_name as _get_config_name, \
    set_config_name as _set_config_name


# Constants
_ALLSET = 0x1f
_ALLCLR_SYNCON = 0x00
_ALLCLR_SYNCOFF = 0x10


class App(_Callback):
    """Main application for handling chromaticity correction."""

    def __init__(self, acc):
        """Class constructor."""
        super().__init__()
        self._pvs_database = _get_database(acc.upper())
        self._ACC = acc.upper()
        if self._ACC == 'BO':
            self._SFAMS = _Const.BO_SFAMS_CHROMCORR
        elif self._ACC == 'SI':
            self._SFAMS = _Const.SI_SFAMS_CHROMCORR

        self._chrom_sp = [0, 0]
        self._chrom_rb = [0, 0]

        self._status = _ALLSET
        self._sfam_check_connection = len(self._SFAMS)*[0]
        self._sfam_check_pwrstate_sts = len(self._SFAMS)*[0]
        self._sfam_check_opmode_sts = len(self._SFAMS)*[-1]
        self._sfam_check_ctrlmode_mon = len(self._SFAMS)*[1]

        self._apply_corr_cmd_count = 0
        self._config_ps_cmd_count = 0
        self._lastcalc_sl = len(self._SFAMS)*[0]

        self._sfam_sl_rb = len(self._SFAMS)*[0]

        if self._ACC == 'SI':
            self._corr_method = _Const.CorrMeth.Proportional
            self._corr_group = _Const.CorrGroup.TwoKnobs
            self._sync_corr = _Const.SyncCorr.Off
            self._config_timing_cmd_count = 0
            self._timing_check_config = 9*[0]
        else:
            self._corr_method = _Const.CorrMeth.Additional
            self._corr_group = _Const.CorrGroup.TwoKnobs
            self._sync_corr = _Const.SyncCorr.Off

        # Get focusing and defocusing families
        sfam_focusing = []
        sfam_defocusing = []
        for fam in self._SFAMS:
            if 'SF' in fam:
                sfam_focusing.append(fam)
            else:
                sfam_defocusing.append(fam)
        sfam_focusing = tuple(sfam_focusing)
        sfam_defocusing = tuple(sfam_defocusing)

        # Initialize correction parameters from local file and configdb
        self.cdb_client = _ConfigDBClient(
            config_type=self._ACC.lower()+'_chromcorr_params')
        [done, corrparams] = self._get_corrparams()
        if done:
            self._config_name = corrparams[0]
            self._nominal_matrix = corrparams[1]
            self._sfam_nomsl = corrparams[2]
            self._nomchrom = corrparams[3]
            self._opticscorr = _OpticsCorr(
                magnetfams_ordering=self._SFAMS,
                nominal_matrix=self._nominal_matrix,
                nominal_intstrengths=self._sfam_nomsl,
                nominal_opticsparam=self._nomchrom,
                magnetfams_focusing=sfam_focusing,
                magnetfams_defocusing=sfam_defocusing)
        else:
            raise Exception(
                "Could not read correction parameters from configdb.")

        # Connect to Sextupoles Families
        self._sfam_sl_sp_pvs = {}
        self._sfam_sl_rb_pvs = {}
        self._sfam_pwrstate_sel_pvs = {}
        self._sfam_pwrstate_sts_pvs = {}
        self._sfam_opmode_sel_pvs = {}
        self._sfam_opmode_sts_pvs = {}
        self._sfam_ctrlmode_mon_pvs = {}

        for fam in self._SFAMS:
            pss = _SiriusPVName(_vaca_prefix+self._ACC+'-Fam:PS-'+fam)
            self._sfam_sl_sp_pvs[fam] = _PV(
                pss.substitute(propty_name='SL', propty_suffix='SP'),
                connection_timeout=0.05)
            self._sfam_sl_rb_pvs[fam] = _PV(
                pss.substitute(propty_name='SL', propty_suffix='RB'),
                callback=self._callback_estimate_chrom,
                connection_callback=self._connection_callback_sfam_sl_rb,
                connection_timeout=0.05)

            self._sfam_pwrstate_sel_pvs[fam] = _PV(
                pss.substitute(propty_name='PwrState', propty_suffix='Sel'),
                connection_timeout=0.05)
            self._sfam_pwrstate_sts_pvs[fam] = _PV(
                pss.substitute(propty_name='PwrState', propty_suffix='Sts'),
                callback=self._callback_sfam_pwrstate_sts,
                connection_timeout=0.05)

            self._sfam_opmode_sel_pvs[fam] = _PV(
                pss.substitute(propty_name='OpMode', propty_suffix='Sel'),
                connection_timeout=0.05)
            self._sfam_opmode_sts_pvs[fam] = _PV(
                pss.substitute(propty_name='OpMode', propty_suffix='Sts'),
                callback=self._callback_sfam_opmode_sts,
                connection_timeout=0.05)

            self._sfam_ctrlmode_mon_pvs[fam] = _PV(
                pss.substitute(propty_name='CtrlMode', propty_suffix='Mon'),
                callback=self._callback_sfam_ctrlmode_mon,
                connection_timeout=0.05)

        # Connect to Timing
        if self._ACC == 'SI':
            SEXTS_TRIG = 'SI-Glob:TI-Mags-Sexts'
            self._timing_sexts_state_sel = _PV(
                _vaca_prefix+SEXTS_TRIG+':State-Sel',
                connection_timeout=0.05)
            self._timing_sexts_state_sts = _PV(
                _vaca_prefix+SEXTS_TRIG+':State-Sts',
                callback=self._callback_timing_state, connection_timeout=0.05)

            self._timing_sexts_polarity_sel = _PV(
                _vaca_prefix+SEXTS_TRIG+':Polarity-Sel',
                connection_timeout=0.05)
            self._timing_sexts_polarity_sts = _PV(
                _vaca_prefix+SEXTS_TRIG+':Polarity-Sts',
                callback=self._callback_timing_state, connection_timeout=0.05)

            self._timing_sexts_src_sel = _PV(
                _vaca_prefix+SEXTS_TRIG+':Src-Sel',
                connection_timeout=0.05)
            self._timing_sexts_src_sts = _PV(
                _vaca_prefix+SEXTS_TRIG+':Src-Sts',
                callback=self._callback_timing_state, connection_timeout=0.05)
            trig_db = _get_trig_db(SEXTS_TRIG)
            try:
                self._chromsi_src_idx = trig_db['Src-Sel']['enums'].index(
                    'ChromSI')
            except Exception:
                self._chromsi_src_idx = 1

            self._timing_sexts_nrpulses_sp = _PV(
                _vaca_prefix+SEXTS_TRIG+':NrPulses-SP',
                connection_timeout=0.05)
            self._timing_sexts_nrpulses_rb = _PV(
                _vaca_prefix+SEXTS_TRIG+':NrPulses-RB',
                callback=self._callback_timing_state, connection_timeout=0.05)

            self._timing_sexts_duration_sp = _PV(
                _vaca_prefix+SEXTS_TRIG+':Duration-SP',
                connection_timeout=0.05)
            self._timing_sexts_duration_rb = _PV(
                _vaca_prefix+SEXTS_TRIG+':Duration-RB',
                callback=self._callback_timing_state, connection_timeout=0.05)

            self._timing_sexts_delay_sp = _PV(
                _vaca_prefix+SEXTS_TRIG+':Delay-SP',
                connection_timeout=0.05)
            self._timing_sexts_delay_rb = _PV(
                _vaca_prefix+SEXTS_TRIG+':Delay-RB',
                callback=self._callback_timing_state, connection_timeout=0.05)

            EVG = _LLTimeSearch.get_evg_name()
            self._timing_evg_chromsimode_sel = _PV(
                _vaca_prefix+EVG+':ChromSIMode-Sel',
                connection_timeout=0.05)
            self._timing_evg_chromsimode_sts = _PV(
                _vaca_prefix+EVG+':ChromSIMode-Sts',
                callback=self._callback_timing_state, connection_timeout=0.05)

            self._timing_evg_chromsidelaytype_sel = _PV(
                _vaca_prefix+EVG+':ChromSIDelayType-Sel',
                connection_timeout=0.05)
            self._timing_evg_chromsidelaytype_sts = _PV(
                _vaca_prefix+EVG+':ChromSIDelayType-Sts',
                callback=self._callback_timing_state, connection_timeout=0.05)

            self._timing_evg_chromsidelay_sp = _PV(
                _vaca_prefix+EVG+':ChromSIDelay-SP',
                connection_timeout=0.05)
            self._timing_evg_chromsidelay_rb = _PV(
                _vaca_prefix+EVG+':ChromSIDelay-RB',
                callback=self._callback_timing_state, connection_timeout=0.05)

            self._timing_evg_chromsiexttrig_cmd = _PV(
                _vaca_prefix+EVG+':ChromSIExtTrig-Cmd',
                connection_timeout=0.05)

    def init_database(self):
        """Set initial PV values."""
        self.run_callbacks('ConfigName-SP', self._config_name)
        self.run_callbacks('ConfigName-RB', self._config_name)
        self.run_callbacks('RespMat-Mon', self._nominal_matrix)
        self.run_callbacks('NominalSL-Mon', self._sfam_nomsl)
        self.run_callbacks('NominalChrom-Mon', self._nomchrom)
        self.run_callbacks('Log-Mon', 'Started.')

    @property
    def pvs_database(self):
        return self._pvs_database

    def process(self, interval):
        """Sleep."""
        t0 = _time.time()
        limit_names = {
            'hilim': 'upper_disp_limit', 'lolim': 'lower_disp_limit',
            'high': 'upper_alarm_limit', 'low': 'lower_alarm_limit',
            'hihi': 'upper_warning_limit', 'lolo': 'lower_warning_limit'}
        if (self._status & 0x1) == 0:  # Check connection
            for fam in self._SFAMS:
                data = self._sfam_sl_rb_pvs[fam].get_ctrlvars()
                if self._sfam_sl_rb_pvs[fam].upper_disp_limit is not None:
                    lis = {k: data[v] for k, v in limit_names.items()}
                    self.run_callbacks('SL'+fam+'-Mon', lis, field='info')
        dt = interval - (_time.time() - t0)
        _time.sleep(max(dt, 0))

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'ChromX-SP':
            self._chrom_sp[0] = value
            self._calc_sl()
            status = True

        elif reason == 'ChromY-SP':
            self._chrom_sp[1] = value
            self._calc_sl()
            status = True

        elif reason == 'ApplyDelta-Cmd':
            done = self._apply_corr()
            if done:
                self._apply_corr_cmd_count += 1
                self.run_callbacks(
                    'ApplyDelta-Cmd', self._apply_corr_cmd_count)

        elif reason == 'ConfigName-SP':
            [done, corrparams] = self._get_corrparams(value)
            if done:
                _set_config_name(
                    acc=self._ACC.lower(), opticsparam='chrom',
                    config_name=value)
                self._config_name = corrparams[0]
                self.run_callbacks('ConfigName-RB', self._config_name)
                self._nominal_matrix = corrparams[1]
                self.run_callbacks('RespMat-Mon', self._nominal_matrix)
                self._sfam_nomsl = corrparams[2]
                self.run_callbacks('NominalSL-Mon', self._sfam_nomsl)
                self._nomchrom = corrparams[3]
                self.run_callbacks('NominalChrom-Mon', self._nomchrom)
                self._opticscorr.nominal_matrix = self._nominal_matrix
                self._opticscorr.nominal_intstrengths = self._sfam_nomsl
                self._opticscorr.nominal_opticsparam = self._nomchrom
                self._calc_sl()
                self.run_callbacks('Log-Mon', 'Updated correction parameters.')
                status = True
            else:
                self.run_callbacks(
                    'Log-Mon', 'ERR:Configuration not found in configdb.')

        elif reason == 'CorrMeth-Sel':
            if value != self._corr_method:
                self._corr_method = value
                self.run_callbacks('CorrMeth-Sts', self._corr_method)
                self._calc_sl()
                status = True

        elif reason == 'CorrGroup-Sel':
            if value != self._corr_group:
                self._corr_group = value
                self.run_callbacks('CorrGroup-Sts', self._corr_group)
                self._calc_sl()
                status = True

        elif reason == 'SyncCorr-Sel':
            if value != self._sync_corr:
                self._sync_corr = value

                if self._config_ps():
                    self._config_ps_cmd_count += 1
                    self.run_callbacks(
                        'ConfigPS-Cmd', self._config_ps_cmd_count)
                if value == 1:
                    if self._config_timing():
                        self._config_timing_cmd_count += 1
                        self.run_callbacks(
                            'ConfigTiming-Cmd', self._config_timing_cmd_count)

                val = 1
                if (self._status & 0x1) == 0:
                    for fam in self._SFAMS:
                        fam_idx = self._SFAMS.index(fam)
                        self._sfam_check_opmode_sts[fam_idx] = \
                            self._sfam_opmode_sts_pvs[fam].value

                    opmode = _PSConst.OpMode.SlowRefSync if value \
                        else _PSConst.OpMode.SlowRef
                    val = any(op != opmode
                              for op in self._sfam_check_opmode_sts)

                self._status = _util.update_bit(
                    v=self._status, bit_pos=2, bit_val=val)

                self.run_callbacks('Status-Mon', self._status)
                self.run_callbacks('SyncCorr-Sts', self._sync_corr)
                status = True

        elif reason == 'ConfigPS-Cmd':
            if self._config_ps():
                self._config_ps_cmd_count += 1
                self.run_callbacks(
                    'ConfigPS-Cmd', self._config_ps_cmd_count)

        elif reason == 'ConfigTiming-Cmd':
            if self._config_timing():
                self._config_timing_cmd_count += 1
                self.run_callbacks(
                    'ConfigTiming-Cmd', self._config_timing_cmd_count)

        return status  # return True to invoke super().write of PCASDriver

    def _get_corrparams(self, config_name=''):
        """Get response matrix from configurations database."""
        try:
            if not config_name:
                config_name = _get_config_name(
                    acc=self._ACC.lower(), opticsparam='chrom')
            params = self.cdb_client.get_config_value(name=config_name)
        except _ConfigDBException:
            return [False, []]

        nom_matrix = [item for sublist in params['matrix'] for item in sublist]
        nom_sl = params['nominal SLs']
        nom_chrom = params['nominal chrom']
        return [True, [config_name, nom_matrix, nom_sl, nom_chrom]]

    def _calc_sl(self):
        delta_chromx = self._chrom_sp[0]-self._chrom_rb[0]
        delta_chromy = self._chrom_sp[1]-self._chrom_rb[1]

        method = 0 \
            if self._corr_method == _Const.CorrMeth.Proportional \
            else 1
        grouping = '2knobs' \
            if self._corr_group == _Const.CorrGroup.TwoKnobs \
            else 'svd'
        lastcalc_deltasl = self._opticscorr.calculate_delta_intstrengths(
            method=method, grouping=grouping,
            delta_opticsparam=[delta_chromx, delta_chromy])

        for fam in self._SFAMS:
            fam_idx = self._SFAMS.index(fam)
            sl_now = self._sfam_sl_rb_pvs[fam].get()
            if sl_now is None:
                return
            self._lastcalc_sl[fam_idx] = sl_now + lastcalc_deltasl[fam_idx]
            self.run_callbacks('SL'+fam+'-Mon', self._lastcalc_sl[fam_idx])

        self.run_callbacks('Log-Mon', 'Calculated SL values.')

    def _apply_corr(self):
        if ((self._status == _ALLCLR_SYNCOFF and
                self._sync_corr == _Const.SyncCorr.Off) or
                self._status == _ALLCLR_SYNCON):
            pvs = self._sfam_sl_sp_pvs
            for fam, pv in pvs.items():
                fam_idx = self._SFAMS.index(fam)
                pv.put(self._lastcalc_sl[fam_idx])
            self.run_callbacks('Log-Mon', 'Applied correction.')

            if self._sync_corr == _Const.SyncCorr.On:
                self._timing_evg_chromsiexttrig_cmd.put(0)
                self.run_callbacks('Log-Mon', 'Generated trigger.')
            return True
        else:
            self.run_callbacks('Log-Mon', 'ERR:ApplyDelta-Cmd failed.')
        return False

    def _connection_callback_sfam_sl_rb(self, pvname, conn, **kws):
        if not conn:
            self.run_callbacks('Log-Mon', 'WARN:'+pvname+' disconnected.')

        fam_idx = self._SFAMS.index(_SiriusPVName(pvname).dev)
        self._sfam_check_connection[fam_idx] = (1 if conn else 0)

        # Change the first bit of correction status
        self._status = _util.update_bit(
            v=self._status, bit_pos=0,
            bit_val=any(s == 0 for s in self._sfam_check_connection))
        self.run_callbacks('Status-Mon', self._status)

    def _callback_estimate_chrom(self, pvname, value, **kws):
        if value is None:
            return
        fam = _SiriusPVName(pvname).dev
        fam_idx = self._SFAMS.index(fam)
        self._sfam_sl_rb[fam_idx] = value

        sfam_deltasl = len(self._SFAMS)*[0]
        for fam in self._SFAMS:
            fam_idx = self._SFAMS.index(fam)
            sfam_deltasl[fam_idx] = \
                self._sfam_sl_rb[fam_idx] - self._sfam_nomsl[fam_idx]

        self._chrom_rb = self._opticscorr.calculate_opticsparam(sfam_deltasl)
        self.run_callbacks('ChromX-RB', self._chrom_rb[0])
        self.run_callbacks('ChromY-RB', self._chrom_rb[1])

    def _callback_sfam_pwrstate_sts(self, pvname, value, **kws):
        if value != _PSConst.PwrStateSts.On:
            self.run_callbacks('Log-Mon', 'WARN:'+pvname+' is Off.')

        fam_idx = self._SFAMS.index(_SiriusPVName(pvname).dev)
        self._sfam_check_pwrstate_sts[fam_idx] = value

        # Change the second bit of correction status
        self._status = _util.update_bit(
            v=self._status, bit_pos=1,
            bit_val=any(s != _PSConst.PwrStateSts.On
                        for s in self._sfam_check_pwrstate_sts))
        self.run_callbacks('Status-Mon', self._status)

    def _callback_sfam_opmode_sts(self, pvname, value, **kws):
        self.run_callbacks('Log-Mon', 'WARN:'+pvname+' changed.')

        fam_idx = self._SFAMS.index(_SiriusPVName(pvname).dev)
        self._sfam_check_opmode_sts[fam_idx] = value

        # Change the third bit of correction status
        opmode = _PSConst.States.SlowRefSync if self._sync_corr \
            else _PSConst.States.SlowRef
        self._status = _util.update_bit(
            v=self._status, bit_pos=2,
            bit_val=any(s != opmode for s in self._sfam_check_opmode_sts))
        self.run_callbacks('Status-Mon', self._status)

    def _callback_sfam_ctrlmode_mon(self,  pvname, value, **kws):
        if value != _PSConst.Interface.Remote:
            self.run_callbacks('Log-Mon', 'WARN:'+pvname+' is not Remote.')

        fam_idx = self._SFAMS.index(_SiriusPVName(pvname).dev)
        self._sfam_check_ctrlmode_mon[fam_idx] = value

        # Change the fourth bit of correction status
        self._status = _util.update_bit(
            v=self._status, bit_pos=3,
            bit_val=any(s != _PSConst.Interface.Remote
                        for s in self._sfam_check_ctrlmode_mon))
        self.run_callbacks('Status-Mon', self._status)

    def _callback_timing_state(self, pvname, value, **kws):
        if 'Sexts:State' in pvname:
            self._timing_check_config[0] = (value == _TIConst.DsblEnbl.Enbl)
        elif 'Sexts:Polarity' in pvname:
            self._timing_check_config[1] = (value == _TIConst.TrigPol.Normal)
        elif 'Sexts:Src' in pvname:
            self._timing_check_config[2] = (value == self._chromsi_src_idx)
        elif 'Sexts:NrPulses' in pvname:
            self._timing_check_config[3] = (value == 1)  # 1 pulse
        elif 'Sexts:Duration' in pvname:
            self._timing_check_config[4] = (value == 150)  # 150us
        elif 'Sexts:Delay' in pvname:
            self._timing_check_config[5] = (value == 0)  # 0us
        elif 'ChromSIMode' in pvname:
            self._timing_check_config[6] = \
                (value == _TIConst.EvtModes.External)
        elif 'ChromSIDelayType' in pvname:
            self._timing_check_config[7] = (
                value == _TIConst.EvtDlyTyp.Incr)
        elif 'ChromSIDelay' in pvname:
            self._timing_check_config[8] = (value == 0)  # 0us

        # Change the fifth bit of correction status
        if self._sync_corr == _Const.SyncCorr.Off:
            bit_val = 0
        else:
            bit_val = any(idx == 0 for idx in self._timing_check_config)
        self._status = _util.update_bit(
            v=self._status, bit_pos=4, bit_val=bit_val)
        self.run_callbacks('Status-Mon', self._status)

    def _config_ps(self):
        opmode = self._sync_corr
        for fam in self._SFAMS:
            if self._sfam_pwrstate_sel_pvs[fam].connected:
                self._sfam_pwrstate_sel_pvs[fam].put(1)
                self._sfam_opmode_sel_pvs[fam].put(opmode)
            else:
                self.run_callbacks('Log-Mon', 'ERR:'+fam+' is disconnected.')
                return False
        self.run_callbacks('Log-Mon', 'Configuration sent to sextupoles.')
        return True

    def _config_timing(self):
        conn = not any(pv.connected is False for pv in [
            self._timing_sexts_state_sel,
            self._timing_sexts_polarity_sel,
            self._timing_sexts_src_sel,
            self._timing_sexts_nrpulses_sp,
            self._timing_sexts_duration_sp,
            self._timing_sexts_delay_sp,
            self._timing_evg_chromsimode_sel,
            self._timing_evg_chromsidelaytype_sel,
            self._timing_evg_chromsidelay_sp])
        if conn:
            self._timing_sexts_state_sel.put(_TIConst.DsblEnbl.Enbl)
            self._timing_sexts_polarity_sel.put(_TIConst.TrigPol.Normal)
            self._timing_sexts_src_sel.put(self._chromsi_src_idx)
            self._timing_sexts_nrpulses_sp.put(1)
            self._timing_sexts_duration_sp.put(0.15)
            self._timing_sexts_delay_sp.put(0)
            self._timing_evg_chromsimode_sel.put(_TIConst.EvtModes.External)
            self._timing_evg_chromsidelaytype_sel.put(_TIConst.EvtDlyTyp.Incr)
            self._timing_evg_chromsidelay_sp.put(0)

            self.run_callbacks('Log-Mon', 'Configuration sent to TI.')
            return True
        else:
            self.run_callbacks('Log-Mon', 'ERR:Some TI PV is disconnected.')
            return False
