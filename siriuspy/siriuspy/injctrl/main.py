"""Main module of Machine Shift Application."""
import time as _time
import logging as _log
import epics as _epics
import numpy as _np

from ..util import update_bit as _updt_bit, get_bit as _get_bit
from ..namesys import SiriusPVName as _PVName
from ..epics import PV as _PV
from ..callbacks import Callback as _Callback
from ..clientarch import Time as _Time

from ..search import PSSearch as _PSSearch, HLTimeSearch as _HLTimeSearch
from ..diagsys.lidiag.csdev import Const as _LIDiagConst, ETypes as _LIDiagEnum
from ..diagsys.psdiag.csdev import ETypes as _PSDiagEnum
from ..diagsys.rfdiag.csdev import Const as _RFDiagConst
from ..devices import InjSysStandbyHandler, EVG, EGun, CurrInfoSI, HLTiming, \
    RFKillBeam, InjSysPUModeHandler

from .csdev import Const as _Const, ETypes as _ETypes, \
    get_injctrl_propty_database as _get_database, \
    get_status_labels as _get_sts_lbls
from .bias_feedback import BiasFeedback as _BiasFeedback


class App(_Callback):
    """Main application for handling machine shift."""

    SCAN_FREQUENCY = 1  # [Hz]

    def __init__(self):
        """Class constructor."""
        super().__init__()
        self._pvs_database = _get_database()

        self._mode = _Const.InjMode.Decay
        self._type = _Const.InjType.MultiBunch
        self._type_mon = _Const.InjTypeMon.Undefined
        self._pumode = _Const.PUMode.Accumulation
        self._pumode_mon = _Const.PUModeMon.Undefined
        self._p2w = {
            'Type': {
                'watcher': None,
                'status': _Const.IdleRunning.Idle
            },
            'FilaOpCurr': {
                'watcher': None,
                'status': _Const.IdleRunning.Idle
            },
            'HVOpVolt': {
                'watcher': None,
                'status': _Const.IdleRunning.Idle
            },
            'PUMode': {
                'watcher': None,
                'status': _Const.IdleRunning.Idle
            },
        }
        self._thread_watdev = None
        self._target_current = 100.0
        self._bucketlist_start = 1
        self._bucketlist_stop = 864
        self._bucketlist_step = 29
        self._isinj_delay = 0
        self._isinj_duration = 300

        self._accum_state_sts = _Const.AccumSts.Off
        self._accum_period = 5  # [s]

        self._topup_state_sts = _Const.TopUpSts.Off
        self._topup_period = 3*60  # [s]
        self._topup_headstarttime = 2.43  # [s]
        self._topup_pustandbyenbl = _Const.DsblEnbl.Dsbl
        self._topup_puwarmuptime = 30
        self._aspu_standby_state = None
        self._topup_liwarmupenbl = _Const.DsblEnbl.Enbl
        self._topup_liwarmuptime = 30
        self._liti_warmup_state = None
        self._topup_bopsstandbyenbl = _Const.DsblEnbl.Dsbl
        self._topup_bopswarmuptime = 10
        self._bops_standby_state = None
        self._topup_borfstandbyenbl = _Const.DsblEnbl.Dsbl
        self._topup_borfwarmuptime = 10
        self._borf_standby_state = None
        now = _Time.now().timestamp()
        self._topup_next = now - (now % (24*60*60)) + 3*60*60
        self._topup_nrpulses = 1
        self._topup_job = None
        self._accum_job = None
        self._abort = False
        self._setting_mode = False

        self._rfkillbeam_mon = _Const.RFKillBeamMon.Idle

        self._thread_autostop = None

        secs = ['LI', 'TB', 'BO', 'TS', 'SI', 'AS']
        self._status = {
            s: self._pvs_database['DiagStatus'+s+'-Mon']['value']
            for s in secs}
        self._status['All'] = self._pvs_database['DiagStatus-Mon']['value']
        self._status_problems = set()
        self._injstatus = self._pvs_database['InjStatus-Mon']['value']

        # use pyepics recommendations for threading
        _epics.ca.use_initial_context()

        # auxiliary diagnosis pvs
        self._pvs_diag = dict()
        for sec in secs:
            self._pvs_diag[sec] = dict()
            self._pvs_diag[sec]['TI'] = {
                n: _PV(n+':Status-Mon', connection_timeout=0.05)
                for n in _HLTimeSearch.get_hl_triggers(filters={'sec': sec})}

            if sec == 'AS':
                continue

            self._pvs_diag[sec]['PS'] = {
                n: _PV(n+':DiagStatus-Mon', connection_timeout=0.05)
                for n in _PSSearch.get_psnames(
                    {'sec': sec, 'dis': 'PS', 'dev': '(B|Q.*|S.*|CH|CV)'})}

            if sec != 'LI':
                punames = _PSSearch.get_psnames({
                    'sec': sec, 'dis': 'PU', 'dev': '.*(Kckr|Sept)',
                    'propty_name': '(?!:CCoil).*'})
                if sec == 'SI':
                    punames.remove('SI-01SA:PU-InjDpKckr')
                self._pvs_diag[sec]['PU'] = {
                    n: _PV(n+':DiagStatus-Mon', connection_timeout=0.05)
                    for n in punames}
            else:
                self._pvs_diag[sec]['PU'] = {
                    n: _PV(n+':DiagStatus-Mon', connection_timeout=0.05)
                    for n in ['LI-01:PU-Modltr-1', 'LI-01:PU-Modltr-2']}

                self._pvs_diag[sec]['RF'] = {
                    n: _PV(n+':DiagStatus-Mon', connection_timeout=0.05)
                    for n in _LIDiagConst.DEV_2_LINAME if 'RF' in n}

                self._pvs_diag[sec]['Egun'] = {
                    n: _PV(n+':DiagStatus-Mon', connection_timeout=0.05)
                    for n in _LIDiagConst.DEV_2_LINAME if 'EG' in n}

            if sec in ['BO', 'SI']:
                self._pvs_diag[sec]['RF'] = {
                    n: _PV(n+':DiagStatus-Mon', connection_timeout=0.05)
                    for n in _RFDiagConst.ALL_DEVICES if n.startswith(sec)}

        # Timing device
        self._hlti_dev = HLTiming()

        # auxiliary injsys PVs
        self._pvs_injsys = dict()
        punames = _PSSearch.get_psnames({
            'sec': '(SI|TS)', 'dev': 'Inj(Sept.*|NLKckr)',
            'propty_name': '(?!:CCoil).*'})
        for pun in punames:
            pv_pulse = _PV(pun+':Pulse-Sts', connection_timeout=0.05)
            pv_trigg = _PV(
                pun.replace('PU', 'TI')+':State-Sts', connection_timeout=0.05)
            self._pvs_injsys[pun] = [pv_pulse, pv_trigg]
        ffname = _HLTimeSearch.get_hl_triggers({'sec': 'SI', 'idx': 'FF.*'})[0]
        self._pvs_injsys[ffname] = [
            _PV(ffname+':State-Sts', connection_timeout=0.05), ]

        # auxiliary devices
        self.egun_dev = EGun(
            print_log=False, callback=self._update_dev_status)
        self._init_egun = False
        self.egun_dev.trigps.pv_object('enable').add_callback(
            self._callback_watch_eguntrig)

        self._pumode_dev = InjSysPUModeHandler(
            print_log=False, callback=self._update_dev_status,
            hltiming=self._hlti_dev)

        self._evg_dev = EVG()
        self._init_injevt = False
        self._evg_dev.pv_object('InjectionEvt-Sel').add_callback(
            self._callback_watch_injectionevt)
        self._evg_dev.set_auto_monitor('TotalInjCount-Mon', True)
        self._evg_dev.pv_object('TotalInjCount-Mon').add_callback(
            self._callback_is_injecting)

        self._injsys_dev = InjSysStandbyHandler(hltiming=self._hlti_dev)

        self.currinfo_dev = CurrInfoSI()
        self.currinfo_dev.set_auto_monitor('Current-Mon', True)
        curr_pvo = self.currinfo_dev.pv_object('Current-Mon')
        curr_pvo.add_callback(self._callback_autostop)
        curr_pvo.connection_callbacks.append(self._callback_conn_autostop)

        self._pu_names, self._pu_devs = list(), list()
        self._pu_refvolt = list()
        for idx, pun in enumerate(self._injsys_dev.handlers['as_pu'].punames):
            # NOTE: The voltage of the TB pulsed magnets are used to define
            # enable conditions of the egun trigger. To avoid changing the
            # trigger enable status during top-up, we will not include these
            # magnets in standby/warm up.
            if pun.startswith('TB'):
                continue
            self._pu_names.append(pun)
            dev = self._injsys_dev.handlers['as_pu'].pudevices[idx]
            self._pu_devs.append(dev)
            pvo = dev.pv_object('Voltage-SP')
            self._pu_refvolt.append(pvo.value)
            pvo.add_callback(self._callback_update_pu_refvolt)

        self._rfkillbeam = RFKillBeam()

        # pvname to write method map
        self.map_pv2write = {
            'Mode-Sel': self.set_mode,
            'Type-Sel': self.set_type,
            'SglBunBiasVolt-SP': self.set_sglbunbiasvolt,
            'MultBunBiasVolt-SP': self.set_multbunbiasvolt,
            'FilaOpCurr-SP': self.set_filaopcurr,
            'HVOpVolt-SP': self.set_hvopvolt,
            'PUMode-Sel': self.set_pumode,
            'PUModeDeltaPosAng-SP': self.set_pumode_delta_posang,
            'PUModeDpKckrDlyRef-SP': self.set_pumode_dpkckr_dlyref,
            'PUModeDpKckrKick-SP': self.set_pumode_dpkckr_kick,
            'TargetCurrent-SP': self.set_target_current,
            'BucketListStart-SP': self.set_bucketlist_start,
            'BucketListStop-SP': self.set_bucketlist_stop,
            'BucketListStep-SP': self.set_bucketlist_step,
            'IsInjDelay-SP': self.set_isinj_delay,
            'IsInjDuration-SP': self.set_isinj_duration,
            'AccumState-Sel': self.set_accum_state,
            'AccumPeriod-SP': self.set_accum_period,
            'TopUpState-Sel': self.set_topup_state,
            'TopUpPeriod-SP': self.set_topup_period,
            'TopUpHeadStartTime-SP': self.set_topup_headstarttime,
            'TopUpPUStandbyEnbl-Sel': self.set_topup_pustandbyenbl,
            'TopUpPUWarmUpTime-SP': self.set_topup_puwarmuptime,
            'TopUpLIWarmUpEnbl-Sel': self.set_topup_liwarmupenbl,
            'TopUpLIWarmUpTime-SP': self.set_topup_liwarmuptime,
            'TopUpBOPSStandbyEnbl-Sel': self.set_topup_bopsstandbyenbl,
            'TopUpBOPSWarmUpTime-SP': self.set_topup_bopswarmuptime,
            'TopUpBORFStandbyEnbl-Sel': self.set_topup_borfstandbyenbl,
            'TopUpBORFWarmUpTime-SP': self.set_topup_borfwarmuptime,
            'TopUpNrPulses-SP': self.set_topup_nrpulses,
            'InjSysTurnOn-Cmd': self.cmd_injsys_turn_on,
            'InjSysTurnOff-Cmd': self.cmd_injsys_turn_off,
            'InjSysTurnOnOrder-SP': self.set_injsys_on_order,
            'InjSysTurnOffOrder-SP': self.set_injsys_off_order,
            'RFKillBeam-Cmd': self.cmd_rfkillbeam,
        }

        # status scanning
        self.quit = False
        self.scanning = False
        self.thread_check_diagstatus = _epics.ca.CAThread(
            target=self._update_diagstatus, daemon=True)
        self.thread_check_diagstatus.start()
        self.thread_check_injstatus = _epics.ca.CAThread(
            target=self._update_injstatus, daemon=True)
        self.thread_check_injstatus.start()

        # initialize default operation values with implemented values
        self.egun_dev.wait_for_connection()
        biasvolt = self.egun_dev.bias.voltage
        if biasvolt is None:
            self._sglbunbiasvolt = _Const.BIAS_SINGLE_BUNCH
            self._multbunbiasvolt = _Const.BIAS_MULTI_BUNCH
        else:
            self._sglbunbiasvolt = biasvolt
            self._multbunbiasvolt = biasvolt
            self.egun_dev.single_bunch_bias_voltage = biasvolt
            self.egun_dev.multi_bunch_bias_voltage = biasvolt
        filacurr = self.egun_dev.fila.current
        if filacurr is None:
            self._filaopcurr = _Const.FILACURR_OPVALUE
        else:
            self._filaopcurr = filacurr
            self.egun_dev.fila_current_opvalue = filacurr
        hvvolt = self.egun_dev.hvps.voltage
        if hvvolt is None:
            self._hvopvolt = _Const.HV_OPVALUE
        else:
            self._hvopvolt = hvvolt
            self.egun_dev.high_voltage_opvalue = hvvolt

        # Create object to make bias feedback:
        self._bias_feedback = _BiasFeedback(self)
        self._pvs_database.update(self._bias_feedback.database)
        for prop, write in self._bias_feedback.map_pv2write.items():
            pvname = _Const.BIASFB_PROPTY_PREFIX + prop
            self.map_pv2write[pvname] = write

    def init_database(self):
        """Set initial PV values."""
        pvn2vals = {
            'Mode-Sel': self._mode,
            'Mode-Sts': self._mode,
            'TypeCmdSts-Mon': self._p2w['Type']['status'],
            'SglBunBiasVolt-SP': self._sglbunbiasvolt,
            'SglBunBiasVolt-RB': self._sglbunbiasvolt,
            'MultBunBiasVolt-SP': self._multbunbiasvolt,
            'MultBunBiasVolt-RB': self._multbunbiasvolt,
            'BiasVoltCmdSts-Mon': _Const.IdleRunning.Idle,
            'FilaOpCurr-SP': self._filaopcurr,
            'FilaOpCurr-RB': self._filaopcurr,
            'FilaOpCurrCmdSts-Mon': self._p2w['FilaOpCurr']['status'],
            'HVOpVolt-SP': self._hvopvolt,
            'HVOpVolt-RB': self._hvopvolt,
            'HVOpVoltCmdSts-Mon': self._p2w['HVOpVolt']['status'],
            'PUModeDeltaPosAng-SP': self._pumode_dev.delta_posang,
            'PUModeDeltaPosAng-RB': self._pumode_dev.delta_posang,
            'PUModeDpKckrDlyRef-SP': self._pumode_dev.dpkckr_dlyref,
            'PUModeDpKckrDlyRef-RB': self._pumode_dev.dpkckr_dlyref,
            'PUModeDpKckrKick-SP': self._pumode_dev.dpkckr_kick,
            'PUModeDpKckrKick-RB': self._pumode_dev.dpkckr_kick,
            'PUModeCmdSts-Mon': self._p2w['PUMode']['status'],
            'TargetCurrent-SP': self._target_current,
            'TargetCurrent-RB': self._target_current,
            'BucketListStart-SP': self._bucketlist_start,
            'BucketListStart-RB': self._bucketlist_start,
            'BucketListStop-SP': self._bucketlist_stop,
            'BucketListStop-RB': self._bucketlist_stop,
            'BucketListStep-SP': self._bucketlist_step,
            'BucketListStep-RB': self._bucketlist_step,
            'IsInjecting-Mon': _Const.IdleInjecting.Idle,
            'IsInjDelay-SP': self._isinj_delay,
            'IsInjDelay-RB': self._isinj_delay,
            'IsInjDuration-SP': self._isinj_duration,
            'IsInjDuration-RB': self._isinj_duration,
            'AccumState-Sel': _Const.OffOn.Off,
            'AccumState-Sts': self._accum_state_sts,
            'AccumPeriod-SP': self._accum_period,
            'AccumPeriod-RB': self._accum_period,
            'TopUpState-Sel': _Const.OffOn.Off,
            'TopUpState-Sts': self._topup_state_sts,
            'TopUpPeriod-SP': self._topup_period/60,
            'TopUpPeriod-RB': self._topup_period/60,
            'TopUpHeadStartTime-SP': self._topup_headstarttime,
            'TopUpHeadStartTime-RB': self._topup_headstarttime,
            'TopUpPUStandbyEnbl-Sel': self._topup_pustandbyenbl,
            'TopUpPUStandbyEnbl-Sts': self._topup_pustandbyenbl,
            'TopUpPUWarmUpTime-SP': self._topup_puwarmuptime,
            'TopUpPUWarmUpTime-RB': self._topup_puwarmuptime,
            'TopUpLIWarmUpEnbl-Sel': self._topup_liwarmupenbl,
            'TopUpLIWarmUpEnbl-Sts': self._topup_liwarmupenbl,
            'TopUpLIWarmUpTime-SP': self._topup_liwarmuptime,
            'TopUpLIWarmUpTime-RB': self._topup_liwarmuptime,
            'TopUpBOPSStandbyEnbl-Sel': self._topup_bopsstandbyenbl,
            'TopUpBOPSStandbyEnbl-Sts': self._topup_bopsstandbyenbl,
            'TopUpBOPSWarmUpTime-SP': self._topup_bopswarmuptime,
            'TopUpBOPSWarmUpTime-RB': self._topup_bopswarmuptime,
            'TopUpBORFStandbyEnbl-Sel': self._topup_bopsstandbyenbl,
            'TopUpBORFStandbyEnbl-Sts': self._topup_bopsstandbyenbl,
            'TopUpBORFWarmUpTime-SP': self._topup_bopswarmuptime,
            'TopUpBORFWarmUpTime-RB': self._topup_bopswarmuptime,
            'TopUpNextInj-Mon': self._topup_next,
            'TopUpNrPulses-SP': self._topup_nrpulses,
            'TopUpNrPulses-RB': self._topup_nrpulses,
            'InjSysCmdDone-Mon': ','.join(self._injsys_dev.done),
            'InjSysCmdSts-Mon': _Const.InjSysCmdSts.Idle,
            'RFKillBeam-Mon': _Const.RFKillBeamMon.Idle,
            'DiagStatusLI-Mon': self._status['LI'],
            'DiagStatusTB-Mon': self._status['TB'],
            'DiagStatusBO-Mon': self._status['BO'],
            'DiagStatusTS-Mon': self._status['TS'],
            'DiagStatusSI-Mon': self._status['SI'],
            'DiagStatus-Mon': self._status['AS'],
            'InjStatus-Mon': self._injstatus,
        }
        for pvn, val in pvn2vals.items():
            self.run_callbacks(pvn, val)

        self._callback_update_type(init=True)
        self.egun_dev.pulse.pv_object('multiselstatus').add_callback(
            self._callback_update_type)
        self.egun_dev.pulse.pv_object('multiswstatus').add_callback(
            self._callback_update_type)
        self.egun_dev.pulse.pv_object('singleselstatus').add_callback(
            self._callback_update_type)
        self.egun_dev.pulse.pv_object('singleswstatus').add_callback(
            self._callback_update_type)
        self.egun_dev.trigmultipre.pv_object('State-Sts').add_callback(
            self._callback_update_type)
        self.egun_dev.trigmulti.pv_object('State-Sts').add_callback(
            self._callback_update_type)
        self.egun_dev.trigsingle.pv_object('State-Sts').add_callback(
            self._callback_update_type)
        self._callback_update_pumode(init=True)
        self._pumode_dev.trigdpk.pv_object('Src-Sts').add_callback(
            self._callback_update_pumode)
        self._pumode_dev.trigdpk.pv_object('DelayRaw-RB').add_callback(
            self._callback_update_pumode)
        self._pumode_dev.pudpk.pv_object('Kick-RB').add_callback(
            self._callback_update_pumode)
        self._pumode_dev.pudpk.pv_object('PwrState-Sts').add_callback(
            self._callback_update_pumode)
        self._pumode_dev.pudpk.pv_object('Pulse-Sts').add_callback(
            self._callback_update_pumode)
        self._pumode_dev.punlk.pv_object('PwrState-Sts').add_callback(
            self._callback_update_pumode)
        self._pumode_dev.punlk.pv_object('Pulse-Sts').add_callback(
            self._callback_update_pumode)
        self._bias_feedback.init_database()
        self.run_callbacks('Log-Mon', 'Started.')

    @property
    def pvs_database(self):
        """Return pvs_database."""
        return self._pvs_database

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        value = None
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        _log.info('Write received for: %s --> %s', reason, str(value))
        if reason in self.map_pv2write.keys():
            status = self.map_pv2write[reason](value)
            _log.info('%s Write for: %s --> %s',
                      str(status).upper(), reason, str(value))
            return status
        _log.warning('PV %s does not have a set function.', reason)
        return False

    # ----- handle writes -----

    def set_mode(self, value):
        """Set injection mode."""
        if not 0 <= value < len(_ETypes.INJMODE):
            return False

        if value == self._mode:
            self.run_callbacks('Mode-Sts', self._mode)
            return True

        # stop topup and accum threads:
        if self._topup_job and self._topup_job.is_alive():
            self._setting_mode = True
            self._stop_topup_job()
            self._setting_mode = False
        if self._accum_job and self._accum_job.is_alive():
            self._setting_mode = True
            self._stop_accum_job()
            self._setting_mode = False

        if self._pumode != _Const.PUMode.Accumulation and \
                value == _Const.InjMode.TopUp:
            self._update_log('ERR:Set PUMode to Accumulation before')
            self._update_log('ERR:changing mode to top-up')
            return False

        if value != _Const.InjMode.Decay:
            stg = 'top-up' if value == _Const.InjMode.TopUp else 'accumulation'
            self._update_log('Configuring EVG RepeatBucketList...')
            self._evg_dev['RepeatBucketList-SP'] = 1
            self._update_log(f'...done. Ready to start {stg:s}.')

        self._mode = value
        self.run_callbacks('Mode-Sts', self._mode)
        return True

    def set_type(self, value):
        """Set injection type."""
        if not 0 <= value < len(_ETypes.INJTYPE):
            return False
        if self._mode != _Const.InjMode.Decay:
            self._update_log('ERR:InjType can only be changed in Decay mode.')
            return False
        if self._p2w['Type']['watcher'] is not None and \
                self._p2w['Type']['watcher'].is_alive():
            self._update_log('WARN:Interrupting type change command..')
            self.egun_dev.cmd_abort_chg_type()
            self._p2w['Type']['watcher'].join()

        self._type = value
        self.run_callbacks('Type-Sts', self._type)

        target = self.egun_dev.cmd_switch_to_single_bunch \
            if value == _Const.InjType.SingleBunch else \
            self.egun_dev.cmd_switch_to_multi_bunch
        self._p2w['Type']['watcher'] = _epics.ca.CAThread(
            target=target, daemon=True)
        self._p2w['Type']['watcher'].start()
        self._p2w['Type']['status'] = _Const.IdleRunning.Running
        self.run_callbacks('TypeCmdSts-Mon', self._p2w['Type']['status'])

        self._launch_watch_dev_thread()
        return True

    def set_sglbunbiasvolt(self, value):
        """Set single bunch bias voltage."""
        self._update_log('Received setpoint to SB Bias voltage.')
        self.egun_dev.single_bunch_bias_voltage = value
        self._sglbunbiasvolt = value
        self.run_callbacks('SglBunBiasVolt-RB', self._sglbunbiasvolt)

        if self._type == _Const.InjType.SingleBunch:
            _epics.ca.CAThread(
                target=self._set_egunbias, args=[value, ], daemon=True).start()
        return True

    def set_multbunbiasvolt(self, value):
        """Set multi bunch bias voltage."""
        self._update_log('Received setpoint to MB Bias voltage.')
        self.egun_dev.multi_bunch_bias_voltage = value
        self._multbunbiasvolt = value
        self.run_callbacks('MultBunBiasVolt-RB', self._multbunbiasvolt)

        if self._type == _Const.InjType.MultiBunch:
            _epics.ca.CAThread(
                target=self._set_egunbias, args=[value, ], daemon=True).start()
        return True

    def _set_egunbias(self, value):
        self.run_callbacks('BiasVoltCmdSts-Mon', _Const.IdleRunning.Running)

        self._update_log(f'Setting EGun Bias voltage to {value:.2f}V...')
        if not self.egun_dev.bias.set_voltage(value, tol=abs(0.005*value)):
            self._update_log('ERR:Could not set EGun Bias voltage.')
        else:
            self._update_log(f'Set EGun Bias voltage: {value:.2f}V.')

        self.run_callbacks('BiasVoltCmdSts-Mon', _Const.IdleRunning.Idle)

    def set_filaopcurr(self, value):
        """Set filament current operation value."""
        if self._p2w['FilaOpCurr']['watcher'] is not None and \
                self._p2w['FilaOpCurr']['watcher'].is_alive():
            self._update_log('WARN:Interrupting FilaPS current ramp...')
            self.egun_dev.cmd_abort_rmp_fila()
            self._p2w['FilaOpCurr']['watcher'].join()

        self.egun_dev.fila_current_opvalue = value
        self._filaopcurr = value
        self.run_callbacks('FilaOpCurr-RB', self._filaopcurr)

        self._p2w['FilaOpCurr']['watcher'] = _epics.ca.CAThread(
            target=self.egun_dev.set_fila_current, daemon=True)
        self._p2w['FilaOpCurr']['watcher'].start()
        self._p2w['FilaOpCurr']['status'] = _Const.IdleRunning.Running
        self.run_callbacks(
            'FilaOpCurrCmdSts-Mon', self._p2w['FilaOpCurr']['status'])

        self._launch_watch_dev_thread()
        return True

    def set_hvopvolt(self, value):
        """Set high voltage operation value."""
        if self._p2w['HVOpVolt']['watcher'] is not None and \
                self._p2w['HVOpVolt']['watcher'].is_alive():
            self._update_log('WARN:Interrupting HVPS voltage ramp...')
            self.egun_dev.cmd_abort_rmp_hvps()
            self._p2w['HVOpVolt']['watcher'].join()

        self.egun_dev.high_voltage_opvalue = value
        self._hvopvolt = value
        self.run_callbacks('HVOpVolt-RB', self._hvopvolt)

        self._p2w['HVOpVolt']['watcher'] = _epics.ca.CAThread(
            target=self.egun_dev.set_hv_voltage, daemon=True)
        self._p2w['HVOpVolt']['watcher'].start()
        self._p2w['HVOpVolt']['status'] = _Const.IdleRunning.Running
        self.run_callbacks(
            'HVOpVoltCmdSts-Mon', self._p2w['HVOpVolt']['status'])

        self._launch_watch_dev_thread()
        return True

    def set_pumode(self, value):
        """Set PU mode."""
        if not 0 <= value < len(_ETypes.PUMODE):
            return False
        if self._mode == _Const.InjMode.TopUp and \
                value != _Const.PUMode.Accumulation:
            self._update_log('ERR:In TopUp mode PUMode must be Accumulation.')
            return False
        if self._p2w['PUMode']['watcher'] is not None and \
                self._p2w['PUMode']['watcher'].is_alive():
            self._update_log('WARN:Interrupting PUMode change command')
            self._pumode_dev.cmd_abort()
            self._p2w['PUMode']['watcher'].join()

        self._pumode = value
        self.run_callbacks('PUMode-Sts', self._pumode)

        target = self._pumode_dev.cmd_switch_to_accum \
            if value == _Const.PUMode.Accumulation else \
            self._pumode_dev.cmd_switch_to_optim \
            if value == _Const.PUMode.Optimization else \
            self._pumode_dev.cmd_switch_to_onaxis
        self._p2w['PUMode']['watcher'] = _epics.ca.CAThread(
            target=target, daemon=True)
        self._p2w['PUMode']['watcher'].start()
        self._p2w['PUMode']['status'] = _Const.IdleRunning.Running
        self.run_callbacks('PUModeCmdSts-Mon', self._p2w['PUMode']['status'])

        self._launch_watch_dev_thread()
        return True

    def set_pumode_delta_posang(self, value):
        """Set PU mode delta posang."""
        self._pumode_dev.delta_posang = value
        self.run_callbacks('PUModeDeltaPosAng-RB', value)
        return True

    def set_pumode_dpkckr_dlyref(self, value):
        """Set PU mode DpKckr delay."""
        self._pumode_dev.dpkckr_dlyref = value
        self.run_callbacks('PUModeDpKckrDlyRef-RB', value)
        return True

    def set_pumode_dpkckr_kick(self, value):
        """Set PU mode DpKckr kick."""
        self._pumode_dev.dpkckr_kick = value
        self.run_callbacks('PUModeDpKckrKick-RB', value)
        return True

    def set_target_current(self, value):
        """Set the target injection current value ."""
        self._target_current = value
        self.run_callbacks('TargetCurrent-RB', self._target_current)
        self._update_log(
            'Updated target current value: {}mA.'.format(value))
        return True

    def set_bucketlist_start(self, start):
        """Set bucketlist_start."""
        if not _Const.MIN_BKT <= start <= _Const.MAX_BKT:
            return False
        stop = self._bucketlist_stop
        step = self._bucketlist_step
        if self._mode == _Const.InjMode.Decay:
            if not self._cmd_bucketlist_fill(stop, start, step):
                return False
        self._bucketlist_start = start
        self.run_callbacks('BucketListStart-RB', start)
        return True

    def set_bucketlist_stop(self, stop):
        """Set bucketlist_stop."""
        if not _Const.MIN_BKT <= stop <= _Const.MAX_BKT:
            return False
        start = self._bucketlist_start
        step = self._bucketlist_step
        if self._mode == _Const.InjMode.Decay:
            if not self._cmd_bucketlist_fill(stop, start, step):
                return False
        self._bucketlist_stop = stop
        self.run_callbacks('BucketListStop-RB', stop)
        return True

    def set_bucketlist_step(self, step):
        """Set bucketlist_step."""
        if not -_Const.MAX_BKT <= step <= _Const.MAX_BKT:
            return False
        if step == 0:
            self._update_log('ERR:Bucket list step must not be zero.')
            return False
        if self._mode != _Const.InjMode.Decay:
            if not self._update_bucket_list(step=step):
                return False
        else:
            start = self._bucketlist_start
            stop = self._bucketlist_stop
            if not self._cmd_bucketlist_fill(stop, start, step):
                return False
        self._bucketlist_step = step
        self.run_callbacks('BucketListStep-RB', step)
        return True

    def set_isinj_delay(self, value):
        """Set IsInjecting-Mon flag delay."""
        if not 0 <= value <= 1000:
            return False
        self._isinj_delay = value
        self._update_log(f'Changed IsInjecting-Mon flag delay to {value}ms.')
        self.run_callbacks('IsInjDelay-RB', value)
        return True

    def set_isinj_duration(self, value):
        """Set IsInjecting-Mon flag duration."""
        if not 0 <= value <= 1000:
            return False
        self._isinj_duration = value
        self._update_log(
            f'Changed IsInjecting-Mon flag duration to {value}ms.')
        self.run_callbacks('IsInjDuration-RB', value)
        return True

    def _cmd_bucketlist_fill(self, stop, start, step):
        """Set bucket list PV."""
        if not self._evg_dev.connected:
            self._update_log('ERR:Could not update bucket list,')
            self._update_log('ERR:EVG is disconnected.')
            return False
        if self._evg_dev.fill_bucketlist(stop, start, step, timeout=3):
            self._update_log('Updated BucketList.')
            return True
        self._update_log('WARN:Timed out waiting for BucketList.')
        return False

    def set_topup_state(self, value):
        """Set top-up state."""
        if self._mode != _Const.InjMode.TopUp:
            return False

        if value == _Const.OffOn.On:
            self._update_log('Start received!')
            if not self._check_allok_2_inject():
                return False
            if self._topup_job is None or not self._topup_job.is_alive():
                self._launch_topup_job()
        else:
            self._update_log('Stop received!')
            if self._topup_job is not None and \
                    self._topup_job.is_alive():
                self._stop_topup_job()
        return True

    def set_accum_state(self, value):
        """Set accum state."""
        if self._mode != _Const.InjMode.Accum:
            return False

        if value == _Const.OffOn.On:
            self._update_log('Start received!')
            if not self._check_allok_2_inject():
                return False
            if self._accum_job is None or not self._accum_job.is_alive():
                self._launch_accum_job()
        else:
            self._update_log('Stop received!')
            if self._accum_job is not None and self._accum_job.is_alive():
                self._stop_accum_job()
        return True

    def set_topup_period(self, value):
        """Set top-up period [min]."""
        if not 1 <= value <= 6*60:
            return False

        sec = value * 60
        if self._topup_state_sts != _Const.TopUpSts.Off:
            now = _Time.now().timestamp()
            self._topup_next = now - (now % sec) + sec
            self.run_callbacks('TopUpNextInj-Mon', self._topup_next)

        self._topup_period = sec
        self._update_log('Changed top-up period to '+str(value)+'min.')
        self.run_callbacks('TopUpPeriod-RB', value)
        return True

    def set_accum_period(self, value):
        """Set accumulation period [s]."""
        if not 1 <= value <= 60*60:
            return False

        self._accum_period = value
        self._update_log('Changed accumulation period to '+str(value)+'s.')
        self.run_callbacks('AccumPeriod-RB', value)
        return True

    def set_topup_headstarttime(self, value):
        """Set top-up head start time [s]."""
        if not 0 <= value <= 2*60:
            return False
        self._topup_headstarttime = value
        self._update_log('Changed top-up head start time to '+str(value)+'s.')
        self.run_callbacks('TopUpHeadStartTime-RB', self._topup_headstarttime)

        minwut = _np.ceil(value+1)
        self._topup_puwarmuptime = max(minwut, self._topup_puwarmuptime)
        self._topup_liwarmuptime = max(minwut, self._topup_liwarmuptime)
        self._topup_bopswarmuptime = max(minwut, self._topup_bopswarmuptime)
        self._topup_borfwarmuptime = max(minwut, self._topup_borfwarmuptime)
        pvn2val = {
            'TopUpPUWarmUpTime-': self._topup_puwarmuptime,
            'TopUpLIWarmUpTime-': self._topup_liwarmuptime,
            'TopUpBOPSWarmUpTime-': self._topup_bopswarmuptime,
            'TopUpBORFWarmUpTime-': self._topup_borfwarmuptime,
        }
        for pvn, val in pvn2val.items():
            self.run_callbacks(pvn+'SP', val)
            self.run_callbacks(pvn+'RB', val)
        return True

    def set_topup_pustandbyenbl(self, value):
        """Enable/disable PU standby between top-up injections."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False

        if value == _Const.DsblEnbl.Dsbl:
            self._handle_aspu_standby_state(_Const.StandbyInject.Inject)
        self._topup_pustandbyenbl = value
        text = 'En' if value else 'Dis'
        self._update_log(text+'abled PU standby between injections.')
        self.run_callbacks('TopUpPUStandbyEnbl-Sts', self._topup_pustandbyenbl)
        return True

    def set_topup_puwarmuptime(self, value):
        """Set PU warm up time before top-up injections."""
        if not self._topup_headstarttime+1 <= value < 2*60:
            return False
        self._topup_puwarmuptime = value
        self.run_callbacks('TopUpPUWarmUpTime-RB', self._topup_puwarmuptime)
        return True

    def set_topup_liwarmupenbl(self, value):
        """Enable/disable LI warm up before top-up injections."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False

        if value == _Const.DsblEnbl.Dsbl:
            self._handle_liti_warmup_state(state=_Const.StandbyInject.Inject)
        self._topup_liwarmupenbl = value
        text = 'En' if value else 'Dis'
        self._update_log(text+'abled LI warm up before injections.')
        self.run_callbacks('TopUpLIWarmUpEnbl-Sts', self._topup_liwarmupenbl)
        return True

    def set_topup_liwarmuptime(self, value):
        """Set LI warm up time before top-up injections."""
        if not self._topup_headstarttime+1 <= value < 2*60:
            return False
        self._topup_liwarmuptime = value
        self.run_callbacks('TopUpLIWarmUpTime-RB', self._topup_liwarmuptime)
        return True

    def set_topup_bopsstandbyenbl(self, value):
        """Enable/disable BO PS standby between top-up injections."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False

        if value == _Const.DsblEnbl.Dsbl:
            self._handle_bops_standby_state(state=_Const.StandbyInject.Inject)
        self._topup_bopsstandbyenbl = value
        text = 'En' if value else 'Dis'
        self._update_log(text+'abled BO PS standby between injections.')
        self.run_callbacks(
            'TopUpBOPSStandbyEnbl-Sts', self._topup_bopsstandbyenbl)
        return True

    def set_topup_bopswarmuptime(self, value):
        """Set BO PS warm up time before top-up injections."""
        if not self._topup_headstarttime+1 <= value < 2*60:
            return False
        self._topup_bopswarmuptime = value
        self.run_callbacks(
            'TopUpBOPSWarmUpTime-RB', self._topup_bopswarmuptime)
        return True

    def set_topup_borfstandbyenbl(self, value):
        """Enable/disable BO RF standby between top-up injections."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False

        if value == _Const.DsblEnbl.Dsbl:
            self._handle_borf_standby_state(state=_Const.StandbyInject.Inject)
        self._topup_borfstandbyenbl = value
        text = 'En' if value else 'Dis'
        self._update_log(text+'abled BO RF standby between injections.')
        self.run_callbacks(
            'TopUpBORFStandbyEnbl-Sts', self._topup_borfstandbyenbl)
        return True

    def set_topup_borfwarmuptime(self, value):
        """Set BO RF warm up time before top-up injections."""
        if not self._topup_headstarttime+1 <= value < 2*60:
            return False
        self._topup_borfwarmuptime = value
        self.run_callbacks(
            'TopUpBORFWarmUpTime-RB', self._topup_borfwarmuptime)
        return True

    def set_topup_nrpulses(self, value):
        """Set top-up number of injection pulses."""
        if not 1 <= value <= 1000:
            return False

        self._topup_nrpulses = value
        if self._mode == _Const.InjMode.TopUp:
            if not self._update_bucket_list():
                return False
        self._update_log('Changed top-up nr.pulses to '+str(value)+'.')
        self.run_callbacks('TopUpNrPulses-RB', self._topup_nrpulses)
        return True

    def cmd_injsys_turn_on(self, value=None, wait_finish=False):
        """Set turn on Injection System."""
        run = self._injsys_dev.is_running
        if run:
            self._update_log('ERR:Still processing turn '+run+' InjSystem')
            return False

        self._update_log('Sending turn on to Inj.System...')
        self.run_callbacks(
            'InjSysCmdDone-Mon', ','.join(self._injsys_dev.done))
        self._injsys_dev.cmd_turn_on(run_in_thread=True)
        thr = _epics.ca.CAThread(
            target=self._watch_injsys, args=['on', ], daemon=True)
        thr.start()
        if wait_finish:
            thr.join()
        return True

    def cmd_injsys_turn_off(self, value=None, wait_finish=False):
        """Set turn off Injection System."""
        run = self._injsys_dev.is_running
        if run:
            self._update_log('ERR:Still processing turn '+run+' InjSystem')
            return False

        self._update_log('Sending turn off to Inj.System...')
        self.run_callbacks(
            'InjSysCmdDone-Mon', ','.join(self._injsys_dev.done))
        self._injsys_dev.cmd_turn_off(run_in_thread=True)
        thr = _epics.ca.CAThread(
            target=self._watch_injsys, args=['off', ], daemon=True)
        thr.start()
        if wait_finish:
            thr.join()
        return True

    def _watch_injsys(self, cmd, timeout=_Const.RF_RMP_TIMEOUT):
        self.run_callbacks(
            'InjSysCmdSts-Mon', getattr(_Const.InjSysCmdSts, cmd.capitalize()))
        _t0 = _time.time()
        while _time.time() - _t0 < timeout:
            if not self._injsys_dev.is_running:
                break
            _time.sleep(0.1)
            self.run_callbacks(
                'InjSysCmdDone-Mon', ','.join(self._injsys_dev.done))
        self.run_callbacks('InjSysCmdSts-Mon', _Const.InjSysCmdSts.Idle)

        is_running = self._injsys_dev.is_running
        ret = self._injsys_dev.result
        if is_running:
            self._update_log('ERR:Timed out in turn '+cmd+' Inj.System.')
            self._injsys_dev.cmd_abort()
        elif not ret[0]:
            self._update_log('ERR:Failed to turn '+cmd+' Inj.System.')
            msgs = ret[1].split('\n')
            msgs = [m[i:i+35] for m in msgs for i in range(0, len(m), 35)]
            for msg in msgs:
                self._update_log('ERR:'+msg)
            self._update_log('ERR:Detail list: ')
            for item in ret[2]:
                self._update_log('ERR:'+item)
        else:
            msg = 'Turned '+cmd+' Inj.System.'
            self._update_log(msg)

    def set_injsys_on_order(self, value):
        """Set inj.sys. turn on command order."""
        new_order = value.split(',')
        if set(new_order) - set(self._injsys_dev.DEF_ON_ORDER):
            self._update_log('ERR:Invalid value for inj.sys. on order')
            return False
        self._injsys_dev.on_order = new_order
        self._update_log('Updated inj.sys. turn on command order.')
        self.run_callbacks('InjSysTurnOnOrder-RB', value)
        return True

    def set_injsys_off_order(self, value):
        """Set inj.sys. turn off command order."""
        new_order = value.split(',')
        if set(new_order) - set(self._injsys_dev.DEF_OFF_ORDER):
            self._update_log('ERR:Invalid value for inj.sys. off order')
            return False
        self._injsys_dev.off_order = new_order
        self._update_log('Updated inj.sys. turn off command order.')
        self.run_callbacks('InjSysTurnOffOrder-RB', value)
        return True

    def cmd_rfkillbeam(self, value):
        """RF Kill Beam command."""
        if self._rfkillbeam_mon == _Const.RFKillBeamMon.Kill:
            self._update_log('ERR:Still processing RFKillBeam command')
            return False

        self._update_log('Received RFKillBeam Command...')
        self._rfkillbeam_mon = _Const.RFKillBeamMon.Kill
        self.run_callbacks('RFKillBeam-Mon', self._rfkillbeam_mon)
        _epics.ca.CAThread(target=self._watch_rfkillbeam, daemon=True).start()
        return True

    def _watch_rfkillbeam(self):
        ret = self._rfkillbeam.cmd_kill_beam()
        if not ret[0]:
            msgs = [ret[1][i:i+35] for i in range(0, len(ret[1]), 35)]
            for msg in msgs:
                self._update_log('ERR:'+msg)
        else:
            self._update_log('The beam was killed by RF!')
        self._rfkillbeam_mon = _Const.RFKillBeamMon.Idle
        self.run_callbacks('RFKillBeam-Mon', self._rfkillbeam_mon)

    # --- callbacks ---

    def _callback_watch_eguntrig(self, value, **kws):
        if not self._init_egun:
            self._init_egun = True
            return
        if self._mode != _Const.InjMode.Decay:
            return
        _epics.ca.CAThread(
            target=self._watch_eguntrig, args=[value, ], daemon=True).start()

    def _watch_eguntrig(self, value, **kws):
        cmd = 'on' if value else 'off'
        _t0 = _time.time()
        while _time.time() - _t0 < 10:
            if self.egun_dev.trigps.is_on() == value:
                msg = 'Turned '+cmd+' EGun.'
                break
            _time.sleep(0.1)
        else:
            msg = 'WARN:Timed out in turn '+cmd+' Egun.'
        self._update_log(msg)

    def _callback_watch_injectionevt(self, value, **kws):
        if not self._init_injevt:
            self._init_injevt = True
            return
        if self._mode != _Const.InjMode.Decay:
            return
        _epics.ca.CAThread(
            target=self._watch_injti, args=[value, ], daemon=True).start()

    def _watch_injti(self, value, timeout=_Const.TI_INJ_TIMEOUT):
        cmd = 'on' if value else 'off'
        _t0 = _time.time()
        while _time.time() - _t0 < timeout:
            if self._evg_dev.injection_state == value:
                msg = 'Turned '+cmd+' InjectionEvt.'
                break
            _time.sleep(0.1)
        else:
            msg = 'WARN:Timed out in turn '+cmd+' InjectionEvt.'
        self._update_log(msg)

    def _callback_autostop(self, value, **kws):
        if self._thread_autostop is not None and \
                self._thread_autostop.is_alive():
            return
        if value is None or value < self._target_current:
            return
        self._thread_autostop = _epics.ca.CAThread(
            target=self._thread_run_autostop, args=[value, 'cb_val'])
        self._thread_autostop.start()

    def _callback_conn_autostop(self, conn, **kws):
        if self._thread_autostop is not None and \
                self._thread_autostop.is_alive():
            return
        if conn:
            return
        self._thread_autostop = _epics.ca.CAThread(
            target=self._thread_run_autostop, args=[conn, 'cb_conn'])
        self._thread_autostop.start()

    def _thread_run_autostop(self, value, cb_type):
        if self._mode != _Const.InjMode.Decay:
            return
        if not self._evg_dev['InjectionEvt-Sel']:
            return
        if not self.egun_dev.trigps.is_on():
            return
        if cb_type == 'cb_val':
            msg = 'Target current reached!'
        else:
            msg = 'ERR:Current PV disconnected.'
        self._update_log(msg)
        self._run_autostop()

    def _run_autostop(self):
        self._update_log('Running Auto Stop...')
        if self._stop_injection():
            self._update_log('Injection Auto Stop done.')
            self._update_bucket_list_autostop()
        else:
            self._update_log('ERR:Injection Auto Stop failed.')

    def _callback_update_type(self, **kws):
        if self.egun_dev.is_single_bunch:
            self._type_mon = _Const.InjTypeMon.SingleBunch
        elif self.egun_dev.is_multi_bunch:
            self._type_mon = _Const.InjTypeMon.MultiBunch
        else:
            self._type_mon = _Const.InjTypeMon.Undefined
        self.run_callbacks('Type-Mon', self._type_mon)

        if 'init' in kws and kws['init']:
            if self._type_mon != _Const.InjTypeMon.Undefined:
                self._type = _ETypes.INJTYPE.index(
                    _ETypes.INJTYPE_MON[self._type_mon])
            self.run_callbacks('Type-Sel', self._type)
            self.run_callbacks('Type-Sts', self._type)

    def _callback_update_pumode(self, **kws):
        if self._pumode_dev.is_accum:
            self._pumode_mon = _Const.PUModeMon.Accumulation
        elif self._pumode_dev.is_optim:
            self._pumode_mon = _Const.PUModeMon.Optimization
        elif self._pumode_dev.is_onaxis:
            self._pumode_mon = _Const.PUModeMon.OnAxis
        else:
            self._pumode_mon = _Const.PUModeMon.Undefined
        self.run_callbacks('PUMode-Mon', self._pumode_mon)

        if 'init' in kws and kws['init']:
            if self._pumode_mon != _Const.PUModeMon.Undefined:
                self._pumode = _ETypes.PUMODE.index(
                    _ETypes.PUMODE_MON[self._pumode_mon])
            self.run_callbacks('PUMode-Sel', self._pumode)
            self.run_callbacks('PUMode-Sts', self._pumode)

    def _callback_update_pu_refvolt(self, pvname, value, **kws):
        if value is None:
            return
        # do not update PU reference voltage if standby is enabled
        if self._topup_pustandbyenbl == _Const.DsblEnbl.Enbl:
            return
        if self._aspu_standby_state == _Const.StandbyInject.Standby:
            return
        devname = _PVName(pvname).device_name
        index = self._pu_names.index(devname)
        self._pu_refvolt[index] = value

    def _callback_is_injecting(self, value, **kws):
        if value is None:
            return
        thread = _epics.ca.CAThread(
            target=self._thread_is_injecting, daemon=True)
        thread.start()

    def _thread_is_injecting(self):
        # check if any InjSI PU is pulsing
        is_injecting = False
        for pvs in self._pvs_injsys.values():
            if not all(pvo.connected for pvo in pvs):
                is_injecting = True  # assume the worst scenario
                break
            if all(pvo.value for pvo in pvs):
                is_injecting = True
                break

        if not is_injecting:
            return

        # if True, raise IsInjecting flag after {delay}ms for {duration}ms
        _time.sleep(self._isinj_delay/1000)
        self.run_callbacks('IsInjecting-Mon', _Const.IdleInjecting.Injecting)
        _time.sleep(self._isinj_duration/1000)
        self.run_callbacks('IsInjecting-Mon', _Const.IdleInjecting.Idle)

    # --- auxiliary injection methods ---

    def _check_allok_2_inject(self, show_warn=True):
        if show_warn:
            if self._status['All'] != 0:
                self._update_log('WARN:DiagStatus not ok:')
                for prob in self._status_problems:
                    self._update_log('WARN:Verify '+prob+'!')

            if self._injstatus != 0:
                self._update_log('WARN:InjStatus not ok:')
                for bit, prob in enumerate(_Const.INJ_STATUS_LABELS):
                    if _get_bit(self._injstatus, bit):
                        self._update_log('WARN:'+prob)

        if self._mode != _Const.InjMode.Decay:
            if self._evg_dev.nrpulses != 1:
                self._update_log('ERR:Aborted. RepeatBucketList must be 1.')
                return False

            if self._abort:
                self._update_log('Abort received.')
                return False
        return True

    def _start_injection(self):
        # turn on injectionevt
        self._update_log('Turning InjectionEvt on...')
        if not self._evg_dev.cmd_turn_on_injection():
            self._update_log('ERR:Could not turn on InjectionEvt.')
            return False
        self._update_log('Sent turn on to InjectionEvt.')

        # wait for injectionevt to be ready
        self._update_log('Waiting for InjectionEvt to be on...')
        _t0 = _time.time()
        while _time.time() - _t0 < _Const.TI_INJ_TIMEOUT:
            if not self._check_allok_2_inject(show_warn=False):
                self._stop_injection()
                return False
            if self._evg_dev.injection_state:
                break
            _time.sleep(0.02)
        else:
            self._update_log('ERR:Timed out waiting for InjectionEvt.')
            return False

        self._update_log('InjectionEvt is on!')
        return True

    def _wait_injection(self):
        # wait for injectionevt to be off (done)
        _t0 = _time.time()
        while _time.time() - _t0 < _Const.MAX_INJTIMEOUT:
            if not self._check_allok_2_inject(show_warn=False):
                self._stop_injection()
                return False
            if not self._evg_dev.injection_state:
                break
            _time.sleep(0.02)
        return True

    def _stop_injection(self):
        self._update_log('Turning off InjectionEvt...')
        if self._evg_dev.cmd_turn_off_injection():
            msg = 'Turned off InjectionEvt.'
        else:
            self._update_log('ERR:Failed to turn off InjectionEvt.')
            self._update_log('Turning off EGun TriggerPS...')
            if self.egun_dev.trigps.cmd_disable_trigger():
                msg = 'Turned off EGun TriggerPS.'
            else:
                msg = 'ERR:Failed to turn off EGun TriggerPS.'
        self._update_log(msg)
        return 'ERR' not in msg

    def _update_bucket_list_autostop(self):
        if not self._evg_dev.connected:
            self._update_log('ERR:Could not update bucket list,')
            self._update_log('ERR:EVG is disconnected.')
            return False
        old_bucklist = self._evg_dev.bucketlist_mon
        injcount = self._evg_dev.injection_count
        blistlen = self._evg_dev.bucketlist_len
        proll = int(injcount % blistlen)
        new_bucklist = _np.roll(old_bucklist, -1 * proll)
        return self._set_bucket_list(new_bucklist)

    def _update_bucket_list(self, step=None, nrpulses=None):
        if not self._evg_dev.connected:
            self._update_log('ERR:Could not update bucket list,')
            self._update_log('ERR:EVG is disconnected.')
            return False

        if step is None:
            step = self._bucketlist_step

        lastfilledbucket = self._evg_dev.bucketlist_mon[-1]
        if not _Const.MIN_BKT <= lastfilledbucket <= _Const.MAX_BKT:
            lastfilledbucket = 1

        nrpulses = nrpulses or self._topup_nrpulses
        bucket = _np.arange(nrpulses) + 1
        bucket *= step
        bucket += lastfilledbucket - 1
        bucket %= 864
        bucket += 1
        return self._set_bucket_list(bucket)

    def _set_bucket_list(self, value):
        self._evg_dev.bucketlist = value
        _t0 = _time.time()
        while _time.time() - _t0 < 5:
            if _np.all(self._evg_dev.bucketlist == value):
                self._update_log('Updated BucketList.')
                return True
        self._update_log('WARN:Could not update BucketList.')
        return False

    # --- auxiliary accumulation methods ---

    def _launch_accum_job(self):
        while self._abort:
            _time.sleep(0.1)
        self._update_log('Launching accumulation thread...')
        self._accum_job = _epics.ca.CAThread(
            target=self._do_accumulation, daemon=True)
        self._accum_job.start()

    def _stop_accum_job(self):
        if self._abort:
            return
        self._update_log('Stopping accumulation thread...')
        self._abort = True
        self._accum_job.join()
        self._accum_job = None
        self._update_log('Stopped accumulation thread.')
        self._abort = False

    def _do_accumulation(self):
        # update bucket list according to settings
        self._update_bucket_list(nrpulses=1)

        self._handle_aspu_standby_state(_Const.StandbyInject.Inject)
        self._handle_liti_warmup_state(_Const.StandbyInject.Inject)
        self._handle_bops_standby_state(_Const.StandbyInject.Inject)
        self._handle_borf_standby_state(_Const.StandbyInject.Inject)

        while self._mode == _Const.InjMode.Accum:
            t0_ = _time.time()
            if not self._continue_accum():
                break

            self.run_callbacks('AccumState-Sts', _Const.AccumSts.TurningOn)
            if not self._start_injection():
                break

            self.run_callbacks('AccumState-Sts', _Const.AccumSts.Injecting)
            if not self._wait_injection():
                break
            self._update_bucket_list(nrpulses=1)

            dt_ = self._accum_period - (_time.time() - t0_)
            if dt_ <= 0:
                continue
            self.run_callbacks('AccumState-Sts', _Const.AccumSts.Waiting)
            self._update_log('Waiting for next injection...')

            while dt_ > 0:
                self.run_callbacks('Log-Mon', f'Remaining time: {dt_:.2f}s')
                slp = min(1, dt_)
                _time.sleep(slp)
                if not self._continue_accum():
                    break
                dt_ = self._accum_period - (_time.time() - t0_)
            else:
                self.run_callbacks('Log-Mon', 'Remaining time: 0s')
                continue
            break

        self._handle_liti_warmup_state(_Const.StandbyInject.Standby)

        # update top-up status
        self.run_callbacks('AccumState-Sts', _Const.AccumSts.Off)
        self._update_log('Stopped accumulation loop.')
        if not self._abort or self._setting_mode:
            self.run_callbacks('AccumState-Sel', _Const.OffOn.Off)

    def _continue_accum(self):
        if not self.currinfo_dev.connected:
            self._update_log('ERR:CurrInfo device disconnected.')
            return False
        if self.currinfo_dev.current >= self._target_current:
            self._update_log(
                'Target Current reached. Stopping accumulation...')
            return False
        if not self._check_allok_2_inject():
            return False
        return True

    # --- auxiliary top-up methods ---

    def _launch_topup_job(self):
        while self._abort:
            _time.sleep(0.1)
        self._update_log('Launching top-up thread...')
        self._topup_job = _epics.ca.CAThread(
            target=self._do_topup, daemon=True)
        self._topup_job.start()

    def _stop_topup_job(self):
        if self._abort:
            return
        self._update_log('Stopping top-up thread...')
        self._abort = True
        self._topup_job.join()
        self._topup_job = None
        self._update_log('Stopped top-up thread.')
        self._abort = False

        # reset next injection schedule
        now = _Time.now().timestamp()
        self._topup_next = now - (now % (24*60*60)) + 3*60*60
        self.run_callbacks('TopUpNextInj-Mon', self._topup_next)

    def _do_topup(self):
        # update bucket list according to settings
        self._update_bucket_list()

        # update next injection schedule
        now, period = _Time.now().timestamp(), self._topup_period
        self._topup_next = now - (now % period) + period
        self.run_callbacks('TopUpNextInj-Mon', self._topup_next)

        # prepare subsystems state
        self._prepare_topup()

        self._bias_feedback.do_update_models = True

        while self._mode == _Const.InjMode.TopUp:
            if not self._check_allok_2_inject():
                break

            self._update_topupsts(_Const.TopUpSts.Waiting)
            self._update_log('Waiting for next injection...')
            if not self._wait_topup_period():
                break
            self._bias_feedback.already_set = False

            self._update_log('Top-up period elapsed. Preparing...')
            if not self.currinfo_dev.connected:
                self._update_log('ERR:CurrInfo device disconnected.')
                break
            if self.currinfo_dev.current < self._target_current * 1.02:
                self._update_topupsts(_Const.TopUpSts.TurningOn)
                self._update_log('Starting injection...')
                if not self._start_injection():
                    break

                self._update_topupsts(_Const.TopUpSts.Injecting)
                self._update_log('Injecting...')
                if not self._wait_injection():
                    break

                self._update_bucket_list()
            else:
                self._update_topupsts(_Const.TopUpSts.Skipping)
                self._update_log('Skipping injection...')
                _time.sleep(2)

            if self._topup_pustandbyenbl:
                self._handle_aspu_standby_state(_Const.StandbyInject.Standby)
            if self._topup_liwarmupenbl:
                self._handle_liti_warmup_state(_Const.StandbyInject.Standby)
            if self._topup_bopsstandbyenbl:
                self._handle_bops_standby_state(_Const.StandbyInject.Standby)
            if self._topup_borfstandbyenbl:
                self._handle_borf_standby_state(_Const.StandbyInject.Standby)

            self._topup_next += self._topup_period
            self.run_callbacks('TopUpNextInj-Mon', self._topup_next)

        self._handle_aspu_standby_state(_Const.StandbyInject.Inject)
        self._handle_liti_warmup_state(_Const.StandbyInject.Standby)
        self._handle_bops_standby_state(_Const.StandbyInject.Inject)
        self._handle_borf_standby_state(_Const.StandbyInject.Inject)

        self._bias_feedback.do_update_models = False

        # update top-up status
        self._update_topupsts(_Const.TopUpSts.Off)
        self._update_log('Stopped top-up loop.')
        if not self._abort or self._setting_mode:
            self.run_callbacks('TopUpState-Sel', _Const.OffOn.Off)

    def _wait_topup_period(self):
        while _time.time() < self._topup_next:
            if not self._check_allok_2_inject(show_warn=False):
                return False
            _time.sleep(1)

            remaining = round(self._topup_next - _time.time())
            text = 'Remaining time: {}s'.format(remaining)
            self.run_callbacks('Log-Mon', text)
            if remaining % 60 == 0:
                _log.info(text)

            # prepare subsystems
            if remaining <= self._topup_puwarmuptime:
                self._handle_aspu_standby_state(_Const.StandbyInject.Inject)
            if remaining <= self._topup_liwarmuptime:
                self._handle_liti_warmup_state(_Const.StandbyInject.Inject)
            if remaining <= self._topup_bopswarmuptime:
                self._handle_bops_standby_state(_Const.StandbyInject.Inject)
            if remaining <= self._topup_borfwarmuptime:
                self._handle_borf_standby_state(_Const.StandbyInject.Inject)

            # bias fb
            cond = remaining <= _Const.BIASFB_AHEADSETIME
            cond &= bool(self._bias_feedback.loop_state)
            cond &= not self._bias_feedback.already_set
            if cond and self.currinfo_dev.connected:
                dcur = self._bias_feedback.get_delta_current_per_pulse(
                    per=self._topup_period, nrpul=self._topup_nrpulses,
                    curr_avg=self._target_current,
                    curr_now=self.currinfo_dev.current,
                    ltime=self.currinfo_dev.lifetime)
                self._update_log(f'BiasFB required InjCurr: {dcur:.3f}mA')
                bias = self._bias_feedback.get_bias_voltage(dcur)
                self.run_callbacks('MultBunBiasVolt-SP', bias)
                self.set_multbunbiasvolt(bias)
                self._bias_feedback.already_set = True

            if _time.time() >= self._topup_next - self._topup_headstarttime:
                return True

        self._update_log('Remaining time: 0s')
        return True

    def _prepare_topup(self):
        # If remaining time is too short do not put in standby or warmup
        # PU
        standby = _Const.StandbyInject.Standby
        if self._topup_pustandbyenbl and \
                self._topup_next - _time.time() > self._topup_puwarmuptime*2:
            self._handle_aspu_standby_state(standby)

        # LI
        if self._topup_liwarmupenbl and \
                self._topup_next - _time.time() > self._topup_liwarmuptime*2:
            self._handle_liti_warmup_state(standby)

        # BO PS
        if self._topup_bopsstandbyenbl and \
                self._topup_next - _time.time() > self._topup_bopswarmuptime*2:
            self._handle_bops_standby_state(standby)

        # BO RF
        if self._topup_borfstandbyenbl and \
                self._topup_next - _time.time() > self._topup_borfwarmuptime*2:
            self._handle_borf_standby_state(standby)

    def _handle_aspu_standby_state(self, state):
        if self._aspu_standby_state == state:
            return
        self._aspu_standby_state = state

        factor = 1 if state == _Const.StandbyInject.Inject else 0.5
        self._update_log(f'Setting PU Voltage to {factor*100}%...')
        for idx, dev in enumerate(self._pu_devs):
            if not dev.connected:
                self._update_log('WARN:'+dev.devname+' disconnected.')
                continue
            dev.voltage = self._pu_refvolt[idx] * factor
        self._update_log('...done.')

    def _handle_liti_warmup_state(self, state):
        if self._liti_warmup_state == state:
            return
        self._liti_warmup_state = state

        lirf = self._injsys_dev.handlers['li_rf']
        if state == _Const.StandbyInject.Inject:
            lirf.change_trigs_to_rmpbo_evt()
        else:
            lirf.change_trigs_to_linac_evt()
        self._update_log('LI timing configured.')

    def _handle_bops_standby_state(self, state):
        if self._bops_standby_state == state:
            return
        self._bops_standby_state = state

        bops = self._injsys_dev.handlers['bo_ps']
        if state == _Const.StandbyInject.Inject:
            bops.enable_triggers()
        else:
            bops.disable_triggers()
        self._update_log('BO PS timing configured.')

    def _handle_borf_standby_state(self, state):
        if self._borf_standby_state == state:
            return
        self._borf_standby_state = state

        borf = self._injsys_dev.handlers['bo_rf']
        if state == _Const.StandbyInject.Inject:
            borf.enable_triggers()
        else:
            borf.disable_triggers()
        self._update_log('BO RF timing configured.')

    # --- auxiliary log methods ---

    def _launch_watch_dev_thread(self):
        if self._thread_watdev is None or not self._thread_watdev.is_alive():
            self._thread_watdev = _epics.ca.CAThread(
                target=self._watch_dev_process, daemon=True)
            self._thread_watdev.start()

    def _watch_dev_process(self):
        running = True
        while running:
            running = True
            for process in self._p2w:
                watcher = self._p2w[process]['watcher']
                status = self._p2w[process]['status']
                watcher_running = watcher is not None and watcher.is_alive()
                if status and not watcher_running:
                    newsts = _Const.IdleRunning.Idle
                    self._p2w[process]['status'] = newsts
                    self.run_callbacks(process+'CmdSts-Mon', newsts)
                running |= watcher_running
            _time.sleep(0.1)

    def _update_dev_status(self, sts, **kws):
        _ = kws
        if 'err:' in sts.lower():
            sts = sts.split(':')[1]
            msgs = ['ERR:'+sts[i:i+35] for i in range(0, len(sts), 35)]
        else:
            msgs = [sts[i:i+39] for i in range(0, len(sts), 39)]
        for msg in msgs:
            self._update_log(msg)

    def _update_log(self, msg):
        if 'ERR' in msg:
            _log.error(msg[4:])
        elif 'FATAL' in msg:
            _log.error(msg[6:])
        elif 'WARN' in msg:
            _log.warning(msg[5:])
        else:
            _log.info(msg)
        self.run_callbacks('Log-Mon', msg)

    def _update_topupsts(self, sts):
        self._topup_state_sts = sts
        self.run_callbacks('TopUpState-Sts', sts)

    # --- auxiliary update status methods ---

    def _update_diagstatus(self):
        """Run as a thread scanning PVs."""
        # constants of alarms to ignore
        psdiag = _PSDiagEnum.DIAG_STATUS_LABELS_AS
        psalrm = int(1 << len(psdiag)) - 1 - int(1 << psdiag.index('Alarms'))
        lipudiag = _LIDiagEnum.DIAG_STATUS_LABELS_PU
        lipualrm = int(1 << len(lipudiag)) - 1
        lipualrm -= int(1 << lipudiag.index('TRIG_Norm not ok'))
        lipualrm -= int(1 << lipudiag.index('Pulse_Current not ok'))

        # scan
        tplanned = 1.0/App.SCAN_FREQUENCY
        while not self.quit:
            if not self.scanning:
                _time.sleep(tplanned)
                continue

            _t0 = _time.time()

            # update sections status
            status_problems = set()
            for sec, sub2pvs in self._pvs_diag.items():
                status_sec = 0
                lbls = _get_sts_lbls(sec)
                for sub, d2pv in sub2pvs.items():
                    if sub not in lbls:
                        continue
                    bit = lbls.index(sub)
                    problems = set()
                    for pvo in d2pv.values():
                        if pvo.connected:
                            value = pvo.value
                            # disregard alarms
                            if sub == 'PS':
                                value = _np.bitwise_and(int(value), psalrm)
                            elif self._mode != _Const.InjMode.Decay and \
                                    sec == 'LI' and sub == 'PU':
                                value = _np.bitwise_and(int(value), lipualrm)
                            nok = value > 0
                        else:
                            nok = True
                        if nok:
                            problems.add(_PVName(pvo.pvname).device_name)
                    val = 1 if problems else 0
                    status_sec = _updt_bit(status_sec, bit, val)
                    if len(problems) > 1:
                        status_problems.add(sec+' '+sub)
                    else:
                        status_problems.update(problems)
                self._status[sec] = status_sec
                self.run_callbacks('DiagStatus'+sec+'-Mon', status_sec)
            self._status_problems = status_problems

            # compile general status
            lbls = _get_sts_lbls()
            status_all = 0
            for bit, sec in enumerate(lbls):
                val = self._status[sec] != 0
                status_all = _updt_bit(status_all, bit, val)
            self._status['All'] = status_all
            self.run_callbacks('DiagStatus-Mon', status_all)

            ttook = _time.time() - _t0
            tsleep = tplanned - ttook
            if tsleep > 0:
                _time.sleep(tsleep)
            else:
                _log.warning(
                    'DiagStatus check took more than planned... '
                    '{0:.3f}/{1:.3f} s'.format(ttook, tplanned))

    def _update_injstatus(self):
        tplanned = 1.0/App.SCAN_FREQUENCY
        while not self.quit:
            if not self.scanning:
                _time.sleep(tplanned)
                continue

            _t0 = _time.time()

            value = 0

            # TI ContinuousEvt is off
            val = 1 if not self._evg_dev.connected else \
                self._evg_dev.continuous_state != 1
            value = _updt_bit(value, 0, val)

            # BucketList not synced
            if self._mode == _Const.InjMode.Decay:
                val = 1 if not self._evg_dev.connected else \
                    self._evg_dev.bucketlist_sync != 1
                value = _updt_bit(value, 1, val)

            if self.egun_dev.connected:
                # EGBiasPS voltage diff. from desired
                volt = self._sglbunbiasvolt \
                    if self._type == _Const.InjType.SingleBunch \
                    else self._multbunbiasvolt
                val = abs(self.egun_dev.bias.voltage_mon - volt) > \
                    self.egun_dev.bias_voltage_tol
                value = _updt_bit(value, 2, val)

                # EGFilaPS current diff. from nominal
                val = not self.egun_dev.is_fila_on
                value = _updt_bit(value, 3, val)

                # EGHVPS voltage diff. from nominal
                val = not self.egun_dev.is_hv_on
                value = _updt_bit(value, 4, val)

                # EGPulsePS setup is diff. from desired
                val = _ETypes.INJTYPE[self._type] != \
                    _ETypes.INJTYPE_MON[self._type_mon]
                value = _updt_bit(value, 5, val)

                # EGTriggerPS is off
                val = not self.egun_dev.trigps.is_on()
                value = _updt_bit(value, 6, val)
            else:
                value = _updt_bit(value, 2, 1)
                value = _updt_bit(value, 3, 1)
                value = _updt_bit(value, 4, 1)
                value = _updt_bit(value, 5, 1)
                value = _updt_bit(value, 6, 1)

            # Inj.System is off
            val = 1 if not self._injsys_dev.connected else \
                not self._injsys_dev.is_on
            value = _updt_bit(value, 7, val)

            self._injstatus = value
            self.run_callbacks('InjStatus-Mon', self._injstatus)

            ttook = _time.time() - _t0
            tsleep = tplanned - ttook
            if tsleep > 0:
                _time.sleep(tsleep)
            else:
                _log.warning(
                    'InjStatus check took more than planned... '
                    '{0:.3f}/{1:.3f} s'.format(ttook, tplanned))
