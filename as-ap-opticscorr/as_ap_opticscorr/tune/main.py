"""Main module of AS-AP-TuneCorr IOC."""

import time as _time
import epics as _epics
import numpy as _np
import siriuspy as _siriuspy
from siriuspy.clientconfigdb import ConfigDBClient as _ConfigDBClient, \
    ConfigDBException as _ConfigDBException
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply.csdev import Const as _PSConst
from siriuspy.timesys.csdev import Const as _TIConst, \
    get_hl_trigger_database as _get_trig_db
from siriuspy.csdevice.opticscorr import Const as _Const
from siriuspy.search import LLTimeSearch as _LLTimeSearch
from siriuspy.optics.opticscorr import OpticsCorr as _OpticsCorr
from as_ap_opticscorr.opticscorr_utils import (
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
        _pvs.print_banner()
        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()
        self._ACC = _pvs.get_pvs_section()
        self._QFAMS = _pvs.get_corr_fams()

        self._driver = driver

        self._delta_tunex = 0.0
        self._delta_tuney = 0.0

        self._status = _ALLSET
        self._qfam_check_connection = len(self._QFAMS)*[0]
        self._qfam_check_pwrstate_sts = len(self._QFAMS)*[0]
        self._qfam_check_opmode_sts = len(self._QFAMS)*[-1]
        self._qfam_check_ctrlmode_mon = len(self._QFAMS)*[1]

        self._set_new_refkl_cmd_count = 0
        self._apply_corr_cmd_count = 0
        self._config_ps_cmd_count = 0
        self._lastcalc_deltakl = len(self._QFAMS)*[0]

        self._qfam_kl_rb = len(self._QFAMS)*[0]

        if self._ACC.lower() == 'si':
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
        qfam_focusing = []
        qfam_defocusing = []
        for fam in self._QFAMS:
            if 'QF' in fam:
                qfam_focusing.append(fam)
            else:
                qfam_defocusing.append(fam)
        qfam_focusing = tuple(qfam_focusing)
        qfam_defocusing = tuple(qfam_defocusing)

        # Initialize correction parameters from local file and configdb
        self.cdb_client = _ConfigDBClient(
            config_type=self._ACC.lower()+'_tunecorr_params')
        [done, corrparams] = self._get_corrparams()
        if done:
            self._config_name = corrparams[0]
            self.driver.setParam('ConfigName-SP', self._config_name)
            self.driver.setParam('ConfigName-RB', self._config_name)
            self._nominal_matrix = corrparams[1]
            self.driver.setParam('RespMat-Mon', self._nominal_matrix)
            self._qfam_nomkl = corrparams[2]
            self.driver.setParam('NominalKL-Mon', self._qfam_nomkl)
            self._opticscorr = _OpticsCorr(
                magnetfams_ordering=self._QFAMS,
                nominal_matrix=self._nominal_matrix,
                nominal_intstrengths=self._qfam_nomkl,
                nominal_opticsparam=[0.0, 0.0],
                magnetfams_focusing=qfam_focusing,
                magnetfams_defocusing=qfam_defocusing)
        else:
            raise Exception(
                "Could not read correction parameters from configdb.")

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
            pss = _SiriusPVName(self._PREFIX_VACA+self._ACC+'-Fam:PS-'+fam)
            self._qfam_kl_sp_pvs[fam] = _epics.PV(
                pss.substitute(propty_name='KL', propty_suffix='SP'))

            self._qfam_refkl[fam] = 0
            self._qfam_kl_rb_pvs[fam] = _epics.PV(
                pss.substitute(propty_name='KL', propty_suffix='RB'),
                callback=[
                    self._callback_init_refkl,
                    self._callback_estimate_deltatune],
                connection_callback=self._connection_callback_qfam_kl_rb)

            self._qfam_pwrstate_sel_pvs[fam] = _epics.PV(
                pss.substitute(propty_name='PwrState', propty_suffix='Sel'))
            self._qfam_pwrstate_sts_pvs[fam] = _epics.PV(
                pss.substitute(propty_name='PwrState', propty_suffix='Sts'),
                callback=self._callback_qfam_pwrstate_sts)

            self._qfam_opmode_sel_pvs[fam] = _epics.PV(
                pss.substitute(propty_name='OpMode', propty_suffix='Sel'))
            self._qfam_opmode_sts_pvs[fam] = _epics.PV(
                pss.substitute(propty_name='OpMode', propty_suffix='Sts'),
                callback=self._callback_qfam_opmode_sts)

            self._qfam_ctrlmode_mon_pvs[fam] = _epics.PV(
                pss.substitute(propty_name='CtrlMode', propty_suffix='Mon'),
                callback=self._callback_qfam_ctrlmode_mon)

        # Connect to Timing
        if self._ACC == 'SI':
            QUADS_TRIG = 'SI-Glob:TI-Mags-Quads'
            trig_db = _get_trig_db(QUADS_TRIG)
            self._tunsi_src_idx = trig_db['Src-Sel']['enums'].index('TunSI')

            self._timing_quads_state_sel = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':State-Sel')
            self._timing_quads_state_sts = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':State-Sts',
                callback=self._callback_timing_state)

            self._timing_quads_polarity_sel = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':Polarity-Sel')
            self._timing_quads_polarity_sts = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':Polarity-Sts',
                callback=self._callback_timing_state)

            self._timing_quads_src_sel = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':Src-Sel')
            self._timing_quads_src_sts = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':Src-Sts',
                callback=self._callback_timing_state)

            self._timing_quads_nrpulses_sp = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':NrPulses-SP')
            self._timing_quads_nrpulses_rb = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':NrPulses-RB',
                callback=self._callback_timing_state)

            self._timing_quads_duration_sp = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':Duration-SP')
            self._timing_quads_duration_rb = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':Duration-RB',
                callback=self._callback_timing_state)

            self._timing_quads_delay_sp = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':Delay-SP')
            self._timing_quads_delay_rb = _epics.PV(
                self._PREFIX_VACA+QUADS_TRIG+':Delay-RB',
                callback=self._callback_timing_state)

            EVG = _LLTimeSearch.get_evg_name()
            self._timing_evg_tunsimode_sel = _epics.PV(
                self._PREFIX_VACA+EVG+':TunSIMode-Sel')
            self._timing_evg_tunsimode_sts = _epics.PV(
                self._PREFIX_VACA+EVG+':TunSIMode-Sts',
                callback=self._callback_timing_state)

            self._timing_evg_tunsidelaytype_sel = _epics.PV(
                self._PREFIX_VACA+EVG+':TunSIDelayType-Sel')
            self._timing_evg_tunsidelaytype_sts = _epics.PV(
                self._PREFIX_VACA+EVG+':TunSIDelayType-Sts',
                callback=self._callback_timing_state)

            self._timing_evg_tunsidelay_sp = _epics.PV(
                self._PREFIX_VACA+EVG+':TunSIDelay-SP')
            self._timing_evg_tunsidelay_rb = _epics.PV(
                self._PREFIX_VACA+EVG+':TunSIDelay-RB',
                callback=self._callback_timing_state)

            self._timing_evg_tunsiexttrig_cmd = _epics.PV(
                self._PREFIX_VACA+EVG+':TunSIExtTrig-Cmd')

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

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'DeltaTuneX-SP':
            self._delta_tunex = value
            self._calc_deltakl()
            status = True

        elif reason == 'DeltaTuneY-SP':
            self._delta_tuney = value
            self._calc_deltakl()
            status = True

        elif reason == 'ApplyDelta-Cmd':
            done = self._apply_corr()
            if done:
                self._apply_corr_cmd_count += 1
                self.driver.setParam(
                    'ApplyDelta-Cmd', self._apply_corr_cmd_count)
                self.driver.updatePV('ApplyDelta-Cmd')

        elif reason == 'ConfigName-SP':
            [done, corrparams] = self._get_corrparams(value)
            if done:
                _set_config_name(
                    acc=self._ACC.lower(), opticsparam='tune',
                    config_name=value)
                self._config_name = corrparams[0]
                self.driver.setParam('ConfigName-RB', self._config_name)
                self._nominal_matrix = corrparams[1]
                self.driver.setParam('RespMat-Mon', self._nominal_matrix)
                self._qfam_nomkl = corrparams[2]
                self.driver.setParam('NominalKL-Mon', self._qfam_nomkl)
                self._opticscorr.nominal_matrix = self._nominal_matrix
                self._opticscorr.nominal_intstrengths = self._qfam_nomkl
                self._calc_deltakl()
                self.driver.setParam(
                    'Log-Mon', 'Updated correction parameters.')
                self.driver.updatePVs()
                status = True
            else:
                self.driver.setParam(
                    'Log-Mon', 'ERR:Configuration not found in configdb.')
                self.driver.updatePV('Log-Mon')

        elif reason == 'CorrMeth-Sel':
            if value != self._corr_method:
                self._corr_method = value
                self.driver.setParam('CorrMeth-Sts', value)
                self.driver.updatePV('CorrMeth-Sts')
                self._calc_deltakl()
                status = True

        elif reason == 'CorrGroup-Sel':
            if value != self._corr_group:
                self._corr_group = value
                self.driver.setParam('CorrGroup-Sts', self._corr_group)
                self.driver.updatePV('CorrGroup-Sts')
                self._calc_deltakl()
                status = True

        elif reason == 'SyncCorr-Sel':
            if value != self._sync_corr:
                self._sync_corr = value

                if self._config_ps():
                    self._config_ps_cmd_count += 1
                    self.driver.setParam(
                        'ConfigPS-Cmd', self._config_ps_cmd_count)

                if value == 1:
                    if self._config_timing():
                        self._config_timing_cmd_count += 1
                        self.driver.setParam(
                            'ConfigTiming-Cmd', self._config_timing_cmd_count)
                val = 1
                if (self._status & 0x1) == 0:
                    for fam in self._QFAMS:
                        fam_idx = self._QFAMS.index(fam)
                        self._qfam_check_opmode_sts[fam_idx] = \
                            self._qfam_opmode_sts_pvs[fam].value

                    opmode = _PSConst.OpMode.SlowRefSync if value \
                        else _PSConst.OpMode.SlowRef
                    val = any(
                        op != opmode for op in self._qfam_check_opmode_sts)

                self._status = _siriuspy.util.update_bit(
                    v=self._status, bit_pos=2, bit_val=val)

                self.driver.setParam('Status-Mon', self._status)
                self.driver.setParam('SyncCorr-Sts', self._sync_corr)
                self.driver.updatePVs()
                status = True

        elif reason == 'ConfigPS-Cmd':
            done = self._config_ps()
            if done:
                self._config_ps_cmd_count += 1
                self.driver.setParam(
                    'ConfigPS-Cmd', self._config_ps_cmd_count)
                self.driver.updatePV('ConfigPS-Cmd')

        elif reason == 'ConfigTiming-Cmd':
            done = self._config_timing()
            if done:
                self._config_timing_cmd_count += 1
                self.driver.setParam(
                    'ConfigTiming-Cmd', self._config_timing_cmd_count)
                self.driver.updatePV('ConfigTiming-Cmd')

        elif reason == 'SetNewRefKL-Cmd':
            self._update_ref()
            self._set_new_refkl_cmd_count += 1
            self.driver.setParam(
                'SetNewRefKL-Cmd', self._set_new_refkl_cmd_count)
            self.driver.updatePV('SetNewRefKL-Cmd')

        return status  # return True to invoke super().write of PCASDriver

    def _get_corrparams(self, config_name=''):
        """Get response matrix from configurations database."""
        try:
            if not config_name:
                config_name = _get_config_name(
                    acc=self._ACC.lower(), opticsparam='tune')
            params = self.cdb_client.get_config_value(name=config_name)
        except _ConfigDBException:
            return [False, []]

        nom_matrix = [item for sublist in params['matrix'] for item in sublist]
        nom_kl = params['nominal KLs']
        return [True, [config_name, nom_matrix, nom_kl]]

    def _calc_deltakl(self):
        method = 0 \
            if self._corr_method == _Const.CorrMeth.Proportional \
            else 1
        grouping = '2knobs' \
            if self._corr_group == _Const.CorrGroup.TwoKnobs \
            else 'svd'
        lastcalc_deltakl = self._opticscorr.calculate_delta_intstrengths(
            method=method, grouping=grouping,
            delta_opticsparam=[self._delta_tunex, self._delta_tuney])

        self.driver.setParam('Log-Mon', 'Calculated KL values.')

        self._lastcalc_deltakl = lastcalc_deltakl
        for fam in self._QFAMS:
            fam_idx = self._QFAMS.index(fam)
            self.driver.setParam(
                'DeltaKL'+fam+'-Mon', self._lastcalc_deltakl[fam_idx])
        self.driver.updatePVs()

    def _apply_corr(self):
        if ((self._status == _ALLCLR_SYNCOFF and
                self._sync_corr == _Const.SyncCorr.Off) or
                self._status == _ALLCLR_SYNCON):
            for fam, pv in self._qfam_kl_sp_pvs.items():
                fam_idx = self._QFAMS.index(fam)
                pv.put(self._qfam_refkl[fam]+self._lastcalc_deltakl[fam_idx])
            self.driver.setParam('Log-Mon', 'Applied correction.')
            self.driver.updatePV('Log-Mon')

            if self._sync_corr == _Const.SyncCorr.On:
                self._timing_evg_tunsiexttrig_cmd.put(0)
                self.driver.setParam('Log-Mon', 'Generated trigger.')
                self.driver.updatePV('Log-Mon')
            return True
        else:
            self.driver.setParam('Log-Mon', 'ERR:ApplyDelta-Cmd failed.')
            self.driver.updatePV('Log-Mon')
        return False

    def _update_ref(self):
        if (self._status & 0x1) == 0:  # Check connection
            # updates reference
            for fam in self._QFAMS:
                value = self._qfam_kl_rb_pvs[fam].get()
                if value is None:
                    return
                self._qfam_refkl[fam] = value
                self.driver.setParam(
                    'RefKL' + fam + '-Mon', self._qfam_refkl[fam])

                fam_idx = self._QFAMS.index(fam)
                self._lastcalc_deltakl[fam_idx] = 0
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
            self.driver.updatePVs()
        else:
            self.driver.setParam(
                'Log-Mon', 'ERR:Some magnet family is disconnected.')
            self.driver.updatePV('Log-Mon')

    def _estimate_current_deltatune(self):
        qfam_deltakl = len(self._QFAMS)*[0]
        for fam in self._QFAMS:
            fam_idx = self._QFAMS.index(fam)
            qfam_deltakl[fam_idx] = \
                self._qfam_kl_rb[fam_idx] - self._qfam_refkl[fam]
        return self._opticscorr.calculate_opticsparam(qfam_deltakl)

    def _callback_init_refkl(self, pvname, value, cb_info, **kws):
        """Initialize RefKL-Mon pvs and remove this callback."""
        # Get reference
        if value is None:
            return
        fam = _SiriusPVName(pvname).dev
        self._qfam_refkl[fam] = value
        self.driver.setParam('RefKL'+fam+'-Mon', self._qfam_refkl[fam])

        # Remove callback
        cb_info[1].remove_callback(cb_info[0])

    def _connection_callback_qfam_kl_rb(self, pvname, conn, **kws):
        if not conn:
            self.driver.setParam('Log-Mon', 'WARN:'+pvname+' disconnected.')
            self.driver.updatePV('Log-Mon')

        fam_idx = self._QFAMS.index(_SiriusPVName(pvname).dev)
        self._qfam_check_connection[fam_idx] = (1 if conn else 0)

        # Change the first bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=0,
            bit_val=any(q == 0 for q in self._qfam_check_connection))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePV('Status-Mon')

    def _callback_estimate_deltatune(self, pvname, value, **kws):
        if value is None:
            return
        fam = _SiriusPVName(pvname).dev
        fam_idx = self._QFAMS.index(fam)

        self._qfam_kl_rb[fam_idx] = value
        delta_tunex, delta_tuney = self._estimate_current_deltatune()
        self.driver.setParam('DeltaTuneX-RB', delta_tunex)
        self.driver.setParam('DeltaTuneY-RB', delta_tuney)
        self.driver.updatePVs()

    def _callback_qfam_pwrstate_sts(self, pvname, value, **kws):
        if value != _PSConst.PwrStateSts.On:
            self.driver.setParam('Log-Mon', 'WARN:'+pvname+' is not On.')
            self.driver.updatePV('Log-Mon')

        fam_idx = self._QFAMS.index(_SiriusPVName(pvname).dev)
        self._qfam_check_pwrstate_sts[fam_idx] = value

        # Change the second bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=1,
            bit_val=any(q != _PSConst.PwrStateSts.On
                        for q in self._qfam_check_pwrstate_sts))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePV('Status-Mon')

    def _callback_qfam_opmode_sts(self, pvname, value, **kws):
        self.driver.setParam('Log-Mon', 'WARN:'+pvname+' changed.')
        self.driver.updatePV('Log-Mon')

        fam_idx = self._QFAMS.index(_SiriusPVName(pvname).dev)
        self._qfam_check_opmode_sts[fam_idx] = value

        # Change the third bit of correction status
        opmode = _PSConst.States.SlowRefSync if self._sync_corr \
            else _PSConst.States.SlowRef
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=2,
            bit_val=any(s != opmode for s in self._qfam_check_opmode_sts))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePV('Status-Mon')

    def _callback_qfam_ctrlmode_mon(self,  pvname, value, **kws):
        if value != _PSConst.Interface.Remote:
            self.driver.setParam('Log-Mon', 'WARN:'+pvname+' is not Remote.')
            self.driver.updatePV('Log-Mon')

        fam_idx = self._QFAMS.index(_SiriusPVName(pvname).dev)
        self._qfam_check_ctrlmode_mon[fam_idx] = value

        # Change the fourth bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=3,
            bit_val=any(q != _PSConst.Interface.Remote
                        for q in self._qfam_check_ctrlmode_mon))
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePV('Status-Mon')

    def _callback_timing_state(self, pvname, value, **kws):
        if 'Quads:State' in pvname:
            self._timing_check_config[0] = (value == _TIConst.DsblEnbl.Enbl)
        elif 'Quads:Polarity' in pvname:
            self._timing_check_config[1] = (value == _TIConst.TrigPol.Normal)
        elif 'Quads:Src' in pvname:
            self._timing_check_config[2] = (value == self._tunsi_src_idx)
        elif 'Quads:NrPulses' in pvname:
            self._timing_check_config[3] = (value == 1)  # 1 pulse
        elif 'Quads:Duration' in pvname:
            self._timing_check_config[4] = \
                _np.isclose(value, 150, atol=0.1)  # 150us
        elif 'Quads:Delay' in pvname:
            self._timing_check_config[5] = \
                _np.isclose(value, 0, atol=0.1)  # 0us
        elif 'TunSIMode' in pvname:
            self._timing_check_config[6] = \
                (value == _TIConst.EvtModes.External)
        elif 'TunSIDelayType' in pvname:
            self._timing_check_config[7] = (
                value == _TIConst.EvtDlyTyp.Incr)
        elif 'TunSIDelay' in pvname:
            self._timing_check_config[8] = \
                _np.isclose(value, 0, atol=0.1)  # 0us

        if self._sync_corr == _Const.SyncCorr.Off:
            bit_val = 0
        else:
            bit_val = any(idx == 0 for idx in self._timing_check_config)

        # Change the fifth bit of correction status
        self._status = _siriuspy.util.update_bit(
            v=self._status, bit_pos=4, bit_val=bit_val)
        self.driver.setParam('Status-Mon', self._status)
        self.driver.updatePV('Status-Mon')

    def _config_ps(self):
        opmode = _PSConst.OpMode.SlowRefSync if self._sync_corr \
            else _PSConst.OpMode.SlowRef
        for fam in self._QFAMS:
            if self._qfam_pwrstate_sel_pvs[fam].connected:
                self._qfam_pwrstate_sel_pvs[fam].put(_PSConst.PwrStateSel.On)
                self._qfam_opmode_sel_pvs[fam].put(opmode)
            else:
                self.driver.setParam(
                    'Log-Mon', 'ERR:'+fam+' is disconnected.')
                self.driver.updatePV('Log-Mon')
                return False
        self.driver.setParam('Log-Mon', 'Configuration sent to quadrupoles.')
        self.driver.updatePV('Log-Mon')
        return True

    def _config_timing(self):
        conn = not any(pv.connected is False for pv in [
            self._timing_quads_state_sel,
            self._timing_quads_polarity_sel,
            self._timing_quads_src_sel,
            self._timing_quads_nrpulses_sp,
            self._timing_quads_duration_sp,
            self._timing_quads_delay_sp,
            self._timing_evg_tunsimode_sel,
            self._timing_evg_tunsidelaytype_sel,
            self._timing_evg_tunsidelay_sp])
        if conn:
            self._timing_quads_state_sel.put(_TIConst.DsblEnbl.Enbl)
            self._timing_quads_polarity_sel.put(_TIConst.TrigPol.Normal)
            self._timing_quads_src_sel.put(self._tunsi_src_idx)
            self._timing_quads_nrpulses_sp.put(1)
            self._timing_quads_duration_sp.put(150)
            self._timing_quads_delay_sp.put(0)
            self._timing_evg_tunsimode_sel.put(_TIConst.EvtModes.External)
            self._timing_evg_tunsidelaytype_sel.put(_TIConst.EvtDlyTyp.Incr)
            self._timing_evg_tunsidelay_sp.put(0)

            self.driver.setParam('Log-Mon', 'Configuration sent to TI.')
            self.driver.updatePV('Log-Mon')
            return True
        else:
            self.driver.setParam('Log-Mon', 'ERR:Some TI PV is disconnected.')
            self.driver.updatePV('Log-Mon')
            return False
