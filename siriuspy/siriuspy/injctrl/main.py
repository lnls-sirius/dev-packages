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
from ..devices import InjSysStandbyHandler, EVG, EGun, CurrInfoSI, MachShift, \
    PowerSupplyPU, RFKillBeam, InjSysPUModeHandler

from .csdev import Const as _Const, ETypes as _ETypes, \
    get_injctrl_propty_database as _get_database, \
    get_status_labels as _get_sts_lbls


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
        self._sglbunbiasvolt = EGun.BIAS_SINGLE_BUNCH
        self._multbunbiasvolt = EGun.BIAS_MULTI_BUNCH
        self._filaopcurr = EGun.FILACURR_OPVALUE
        self._hvopvolt = EGun.HV_OPVALUE
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
        self._bucketlist_step = 15

        self._topupstate_sel = _Const.OffOn.Off
        self._topupstate_sts = _Const.TopUpSts.Off
        self._topupperiod = 5*60  # [s]
        self._topupheadstarttime = 0
        self._topuppustandbyenbl = _Const.DsblEnbl.Dsbl
        now = _Time.now().timestamp()
        self._topupnext = now - (now % (24*60*60)) + 3*60*60
        self._topupnrpulses = 1
        self._topup_thread = None
        self._topup_pu_prepared = False
        self._autostop = _Const.OffOn.Off
        self._abort = False

        self._injsys_turn_on_count = 0
        self._injsys_turn_off_count = 0

        self._rfkillbeam_mon = _Const.RFKillBeamMon.Idle
        self._rfkillbeam_count = 0

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
                punames = _PSSearch.get_psnames(
                    {'sec': sec, 'dis': 'PU', 'dev': '.*(Kckr|Sept)'})
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

        # auxiliary devices
        self._egun_dev = EGun(
            print_log=False, callback=self._update_dev_status)
        self._init_egun = False
        self._egun_dev.trigps.pv_object('enable').add_callback(
            self._callback_watch_eguntrig)
        self._egun_dev.trigps.pv_object('enablereal').add_callback(
            self._callback_autostop)

        self._pumode_dev = InjSysPUModeHandler(
            print_log=False, callback=self._update_dev_status)

        self._evg_dev = EVG()
        self._init_injevt = False
        self._evg_dev.pv_object('InjectionEvt-Sel').add_callback(
            self._callback_watch_injectionevt)
        self._evg_dev.pv_object('InjectionEvt-Sel').add_callback(
            self._callback_autostop)
        self._evg_dev.pv_object('RepeatBucketList-RB').add_callback(
            self._callback_watch_repeatbucketlist)

        self._injsys_dev = InjSysStandbyHandler()

        self._currinfo_dev = CurrInfoSI()

        self._pu_names = _PSSearch.get_psnames(
            {'dis': 'PU', 'dev': '.*(InjKckr|EjeKckr|InjNLKckr|Sept)'})
        self._pu_devs = [PowerSupplyPU(pun) for pun in self._pu_names]
        self._pu_refvolt = list()
        self._topup_puref_ignore = False
        for dev in self._pu_devs:
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
            'TargetCurrent-SP': self.set_target_current,
            'BucketListStart-SP': self.set_bucketlist_start,
            'BucketListStop-SP': self.set_bucketlist_stop,
            'BucketListStep-SP': self.set_bucketlist_step,
            'TopUpState-Sel': self.set_topupstate,
            'TopUpPeriod-SP': self.set_topupperiod,
            'TopUpHeadStartTime-SP': self.set_topupheadstarttime,
            'TopUpPUStandbyEnbl-Sel': self.set_topuppustandbyenbl,
            'TopUpNrPulses-SP': self.set_topupnrpulses,
            'AutoStop-Sel': self.set_autostop,
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

    def init_database(self):
        """Set initial PV values."""
        self.run_callbacks('Mode-Sel', self._mode)
        self.run_callbacks('Mode-Sts', self._mode)
        self._callback_update_type(init=True)
        self._egun_dev.pulse.pv_object('multiselstatus').add_callback(
            self._callback_update_type)
        self._egun_dev.pulse.pv_object('multiswstatus').add_callback(
            self._callback_update_type)
        self._egun_dev.pulse.pv_object('singleselstatus').add_callback(
            self._callback_update_type)
        self._egun_dev.pulse.pv_object('singleswstatus').add_callback(
            self._callback_update_type)
        self._egun_dev.trigmultipre.pv_object('State-Sts').add_callback(
            self._callback_update_type)
        self._egun_dev.trigmulti.pv_object('State-Sts').add_callback(
            self._callback_update_type)
        self._egun_dev.trigsingle.pv_object('State-Sts').add_callback(
            self._callback_update_type)
        self.run_callbacks('TypeCmdSts-Mon', self._p2w['Type']['status'])
        self.run_callbacks('SglBunBiasVolt-SP', self._sglbunbiasvolt)
        self.run_callbacks('SglBunBiasVolt-RB', self._sglbunbiasvolt)
        self.run_callbacks('MultBunBiasVolt-SP', self._multbunbiasvolt)
        self.run_callbacks('MultBunBiasVolt-RB', self._multbunbiasvolt)
        self.run_callbacks('BiasVoltCmdSts-Mon', _Const.IdleRunning.Idle)
        self.run_callbacks('FilaOpCurr-SP', self._filaopcurr)
        self.run_callbacks('FilaOpCurr-RB', self._filaopcurr)
        self.run_callbacks(
            'FilaOpCurrCmdSts-Mon', self._p2w['FilaOpCurr']['status'])
        self.run_callbacks('HVOpVolt-SP', self._hvopvolt)
        self.run_callbacks('HVOpVolt-RB', self._hvopvolt)
        self.run_callbacks(
            'HVOpVoltCmdSts-Mon', self._p2w['HVOpVolt']['status'])
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
        self.run_callbacks('PUModeCmdSts-Mon', self._p2w['PUMode']['status'])
        self.run_callbacks('TargetCurrent-SP', self._target_current)
        self.run_callbacks('TargetCurrent-RB', self._target_current)
        self.run_callbacks('BucketListStart-SP', self._bucketlist_start)
        self.run_callbacks('BucketListStart-RB', self._bucketlist_start)
        self.run_callbacks('BucketListStop-SP', self._bucketlist_stop)
        self.run_callbacks('BucketListStop-RB', self._bucketlist_stop)
        self.run_callbacks('BucketListStep-SP', self._bucketlist_step)
        self.run_callbacks('BucketListStep-RB', self._bucketlist_step)
        self.run_callbacks('TopUpState-Sel', self._topupstate_sel)
        self.run_callbacks('TopUpState-Sts', self._topupstate_sts)
        self.run_callbacks('TopUpPeriod-SP', self._topupperiod/60)
        self.run_callbacks('TopUpPeriod-RB', self._topupperiod/60)
        self.run_callbacks('TopUpHeadStartTime-SP', self._topupheadstarttime)
        self.run_callbacks('TopUpHeadStartTime-RB', self._topupheadstarttime)
        self.run_callbacks('TopUpPUStandbyEnbl-Sel', self._topuppustandbyenbl)
        self.run_callbacks('TopUpPUStandbyEnbl-Sts', self._topuppustandbyenbl)
        self.run_callbacks('TopUpNextInj-Mon', self._topupnext)
        self.run_callbacks('TopUpNrPulses-SP', self._topupnrpulses)
        self.run_callbacks('TopUpNrPulses-RB', self._topupnrpulses)
        self.run_callbacks('AutoStop-Sel', self._autostop)
        self.run_callbacks('AutoStop-Sts', self._autostop)
        self.run_callbacks('InjSysTurnOn-Cmd', self._injsys_turn_on_count)
        self.run_callbacks('InjSysTurnOff-Cmd', self._injsys_turn_off_count)
        self.run_callbacks(
            'InjSysCmdDone-Mon', ','.join(self._injsys_dev.done))
        self.run_callbacks('InjSysCmdSts-Mon', _Const.InjSysCmdSts.Idle)
        self.run_callbacks('RFKillBeam-Cmd', self._rfkillbeam_count)
        self.run_callbacks('RFKillBeam-Mon', _Const.RFKillBeamMon.Idle)
        self.run_callbacks('DiagStatusLI-Mon', self._status['LI'])
        self.run_callbacks('DiagStatusTB-Mon', self._status['TB'])
        self.run_callbacks('DiagStatusBO-Mon', self._status['BO'])
        self.run_callbacks('DiagStatusTS-Mon', self._status['TS'])
        self.run_callbacks('DiagStatusSI-Mon', self._status['SI'])
        self.run_callbacks('DiagStatus-Mon', self._status['AS'])
        self.run_callbacks('InjStatus-Mon', self._injstatus)
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

        if value == _Const.InjMode.TopUp and \
                self._topupstate_sts == _Const.TopUpSts.Off:
            self._update_log('Configuring EVG RepeatBucketList...')
            self._evg_dev['RepeatBucketList-SP'] = 1
            self._update_log('...done. Waiting to start top-up.')
        else:
            if self._topup_thread and self._topup_thread.is_alive():
                self._stop_topup_thread()

        self._mode = value
        self.run_callbacks('Mode-Sts', self._mode)
        return True

    def set_type(self, value):
        """Set injection type."""
        if not 0 <= value < len(_ETypes.INJTYPE):
            return False
        if self._mode == _Const.InjMode.TopUp:
            self._update_log(
                'ERR:Turn off top-up mode before changing inj.type.')
            return False
        if self._p2w['Type']['watcher'] is not None and \
                self._p2w['Type']['watcher'].is_alive():
            self._update_log('WARN:Interrupting type change command..')
            self._egun_dev.cmd_abort_chg_type()
            self._p2w['Type']['watcher'].join()

        self._type = value
        self.run_callbacks('Type-Sts', self._type)

        target = self._egun_dev.cmd_switch_to_single_bunch \
            if value == _Const.InjType.SingleBunch else \
            self._egun_dev.cmd_switch_to_multi_bunch
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
        self._egun_dev.single_bunch_bias_voltage = value
        self._sglbunbiasvolt = value
        self.run_callbacks('SglBunBiasVolt-RB', self._sglbunbiasvolt)

        if self._type == _Const.InjType.SingleBunch:
            _epics.ca.CAThread(
                target=self._set_egunbias, args=[value, ], daemon=True).start()
        return True

    def set_multbunbiasvolt(self, value):
        """Set multi bunch bias voltage."""
        self._update_log('Received setpoint to MB Bias voltage.')
        self._egun_dev.multi_bunch_bias_voltage = value
        self._multbunbiasvolt = value
        self.run_callbacks('MultBunBiasVolt-RB', self._multbunbiasvolt)

        if self._type == _Const.InjType.MultiBunch:
            _epics.ca.CAThread(
                target=self._set_egunbias, args=[value, ], daemon=True).start()
        return True

    def _set_egunbias(self, value):
        self.run_callbacks('BiasVoltCmdSts-Mon', _Const.IdleRunning.Running)

        self._update_log('Setting EGun Bias voltage to {}V...'.format(value))
        if not self._egun_dev.bias.set_voltage(value):
            self._update_log('ERR:Could not set EGun Bias voltage.')
        else:
            self._update_log('Set EGun Bias voltage: {}V.'.format(value))

        self.run_callbacks('BiasVoltCmdSts-Mon', _Const.IdleRunning.Idle)

    def set_filaopcurr(self, value):
        """Set filament current operation value."""
        if self._p2w['FilaOpCurr']['watcher'] is not None and \
                self._p2w['FilaOpCurr']['watcher'].is_alive():
            self._update_log('WARN:Interrupting FilaPS current ramp...')
            self._egun_dev.cmd_abort_rmp_fila()
            self._p2w['FilaOpCurr']['watcher'].join()

        self._egun_dev.fila_current_opvalue = value
        self._filaopcurr = value
        self.run_callbacks('FilaOpCurr-RB', self._filaopcurr)

        self._p2w['FilaOpCurr']['watcher'] = _epics.ca.CAThread(
            target=self._egun_dev.set_fila_current, daemon=True)
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
            self._egun_dev.cmd_abort_rmp_hvps()
            self._p2w['HVOpVolt']['watcher'].join()

        self._egun_dev.high_voltage_opvalue = value
        self._hvopvolt = value
        self.run_callbacks('HVOpVolt-RB', self._hvopvolt)

        self._p2w['HVOpVolt']['watcher'] = _epics.ca.CAThread(
            target=self._egun_dev.set_hv_voltage, daemon=True)
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
        if self._mode == _Const.InjMode.TopUp:
            self._update_log(
                'ERR:Turn off top-up mode before changing PUMode.')
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
        if not self._cmd_bucketlist_fill(stop, start, step):
            return False
        self._bucketlist_stop = stop
        self.run_callbacks('BucketListStop-RB', stop)
        return True

    def set_bucketlist_step(self, step):
        """Set bucketlist_step."""
        if not -_Const.MAX_BKT+1 <= step <= _Const.MAX_BKT-1:
            return False
        if self._mode == _Const.InjMode.TopUp:
            bucket = _np.arange(self._topupnrpulses) + 1
            bucket *= step
            bucket += self._evg_dev.bucketlist[0] - 1
            bucket %= 864
            bucket += 1
            if not self._set_bucket_list(bucket):
                return False
        else:
            start = self._bucketlist_start
            stop = self._bucketlist_stop
            if not self._cmd_bucketlist_fill(stop, start, step):
                return False
        self._bucketlist_step = step
        self.run_callbacks('BucketListStep-RB', step)
        return True

    def _cmd_bucketlist_fill(self, stop, start, step):
        """Set bucket list PV."""
        if self._evg_dev.fill_bucketlist(stop, start, step, timeout=3):
            self._update_log('Updated BucketList.')
            return True
        self._update_log('WARN:Timed out waiting for BucketList.')
        return False

    def set_topupstate(self, value):
        """Set top-up state."""
        if self._mode != _Const.InjMode.TopUp:
            return

        self._topupstate_sel = value
        if value == _Const.OffOn.On:
            self._update_log('Start received!')
            if not self._check_allok_2_inject():
                return
            if self._topup_thread is not None and \
                    not self._topup_thread.is_alive() or\
                    self._topup_thread is None:
                self._launch_topup_thread()
        else:
            self._update_log('Stop received!')
            if self._topup_thread is not None and \
                    self._topup_thread.is_alive():
                self._stop_topup_thread()

        return True

    def set_topupperiod(self, value):
        """Set top-up period [min]."""
        if not 1 <= value <= 6*60:
            return False

        sec = value*60
        if self._topupstate_sts != _Const.TopUpSts.Off:
            now = _Time.now().timestamp()
            self._topupnext = now - (now % sec) + sec
            self.run_callbacks('TopUpNextInj-Mon', self._topupnext)

        self._topupperiod = sec
        self._update_log('Changed top-up period to '+str(value)+'min.')
        self.run_callbacks('TopUpPeriod-RB', value)
        return True

    def set_topupheadstarttime(self, value):
        """Set top-up head start time [s]."""
        if not 0 <= value <= 10*60:
            return False

        self._topupheadstarttime = value
        self._update_log('Changed top-up head start time to '+str(value)+'s.')
        self.run_callbacks('TopUpHeadStartTime-RB', self._topupheadstarttime)
        return True

    def set_topuppustandbyenbl(self, value):
        """Set PU standby between top-up injections."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False

        if value:
            if not self._update_topup_pu_refvolt():
                return False
        else:
            self._prepare_topup('inject')
        self._topuppustandbyenbl = value
        text = 'En' if value else 'Dis'
        self._update_log(text+'abled PU standby between injections.')
        self.run_callbacks('TopUpPUStandbyEnbl-Sts', self._topuppustandbyenbl)
        return True

    def set_topupnrpulses(self, value):
        """Set top-up number of injection pulses."""
        if not 1 <= value <= 1000:
            return False

        self._topupnrpulses = value
        if self._mode == _Const.InjMode.TopUp:
            bucket = _np.arange(self._topupnrpulses) + 1
            bucket *= self._bucketlist_step
            bucket += self._evg_dev.bucketlist[0] - 1
            bucket %= 864
            bucket += 1
            self._set_bucket_list(bucket)
        self._update_log('Changed top-up nr.pulses to '+str(value)+'.')
        self.run_callbacks('TopUpNrPulses-RB', self._topupnrpulses)
        return True

    def set_autostop(self, value):
        """Set Auto Stop."""
        if not 0 <= value < len(_ETypes.OFF_ON):
            return False
        if self._evg_dev.nrpulses != 0:
            self._update_log('ERR:Could not turn on AutoStop. Set ')
            self._update_log('ERR:RepeatBucketList to 0 to continue.')
            return False
        self._autostop = value
        self.run_callbacks('AutoStop-Sts', self._autostop)
        self._update_log(
            'Turned '+_ETypes.OFF_ON[value]+' Auto Stop.')
        self._callback_autostop()
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

        self._injsys_turn_on_count += 1
        self.run_callbacks('InjSysTurnOn-Cmd', self._injsys_turn_on_count)
        return False

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

        self._injsys_turn_off_count += 1
        self.run_callbacks('InjSysTurnOff-Cmd', self._injsys_turn_off_count)
        return False

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
        ret = self._injsys_dev.result
        if ret is None:
            msg = 'ERR:Timed out in turn '+cmd+' Inj.System.'
        elif not ret[0]:
            self._update_log('ERR:Failed to turn '+cmd+' Inj.System.')
            msgs = [ret[1][i:i+35] for i in range(0, len(ret[1]), 35)]
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

        self._rfkillbeam_count += 1
        self.run_callbacks('RFKillBeam-Cmd', self._rfkillbeam_count)
        return False

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
        if self._mode == _Const.InjMode.TopUp:
            return
        _epics.ca.CAThread(
            target=self._watch_eguntrig, args=[value, ], daemon=True).start()

    def _watch_eguntrig(self, value, **kws):
        cmd = 'on' if value else 'off'
        _t0 = _time.time()
        while _time.time() - _t0 < 10:
            if self._egun_dev.trigps.is_on() == value:
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
        if self._mode == _Const.InjMode.TopUp:
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

    def _callback_autostop(self, **kws):
        if self._mode == _Const.InjMode.TopUp:
            return
        if self._autostop == _Const.OffOn.Off:
            return
        if not self._evg_dev['InjectionEvt-Sel']:
            return
        if not self._egun_dev.trigps.is_on():
            return

        _epics.ca.CAThread(target=self._run_autostop, daemon=True).start()

    def _run_autostop(self):
        self._update_log('Injection Auto Stop activated...')
        if not self._wait_autostop():
            self._update_log('Injection Auto Stop Routine aborted.')
            return

        if self._stop_injection():
            self._update_log('Injection Auto Stop done.')
            self._update_bucket_list_autostop()
        else:
            self._update_log('Injection Auto Stop failed.')

    def _wait_autostop(self):
        if not self._injsys_dev.is_on:
            self._update_log('Waiting for Inj.System to be on...')
            _t0 = _time.time()
            while _time.time() - _t0 < _Const.RF_RMP_TIMEOUT:
                if self._autostop == _Const.OffOn.Off:
                    return False
                if self._injsys_dev.is_on:
                    self._update_log('Inj.System is on.')
                    break
                else:
                    # handle a timing configuration that do not use InjBO evt
                    states = self._injsys_dev.get_dev_state(
                        ['bo_rf', 'as_pu', 'bo_ps', 'li_rf'])
                    if all(states):
                        self._update_log('Ignoring InjBO event off state...')
                        self._update_log('...Inj.System is on.')
                        break
            else:
                self._update_log('ERR:Timed out waiting for Inj.Sys.')
                return False

        self._update_log('Waiting for InjectionEvt to be on...')
        _t0 = _time.time()
        while _time.time() - _t0 < _Const.TI_INJ_TIMEOUT:
            if self._autostop == _Const.OffOn.Off \
                    or not self._evg_dev['InjectionEvt-Sel']:
                return False
            if self._evg_dev.injection_state:
                self._update_log('InjectionEvt is on.')
                break
        else:
            self._update_log('ERR:Timed out waiting for InjectionEvt.')
            return False

        self._update_log('Waiting for current to reach target value...')
        return self._wait_injection()

    def _callback_update_type(self, **kws):
        if self._egun_dev.is_single_bunch:
            self._type_mon = _Const.InjTypeMon.SingleBunch
        elif self._egun_dev.is_multi_bunch:
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

    def _callback_watch_repeatbucketlist(self, value, **kws):
        if self._mode == _Const.InjMode.TopUp:
            if value != 1:
                self._update_log('WARN:RepeatBucketList is diff. from 1.')
                self._update_log('WARN:Aborting top-up...')
            return
        if self._autostop == _Const.OffOn.On and value != 0:
            self._autostop = _Const.OffOn.Off
            self.run_callbacks('AutoStop-Sel', self._autostop)
            self.run_callbacks('AutoStop-Sts', self._autostop)
            self._update_log('WARN:RepeatBucketList is diff. from 0.')
            self._update_log('WARN:Turned Off Auto Stop.')

    def _callback_update_pu_refvolt(self, pvname, value, **kws):
        if value is None:
            return
        if self._topup_puref_ignore:
            return
        devname = _PVName(pvname).device_name
        index = self._pu_names.index(devname)
        self._pu_refvolt[index] = value

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

        if self._mode == _Const.InjMode.TopUp:
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
                self._abort_injection()
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
        init_mode, init_autostop = self._mode, self._autostop
        if init_mode == _Const.InjMode.TopUp:
            # if in TopUp mode, wait for injectionevt to be off (done)
            _t0 = _time.time()
            while _time.time() - _t0 < _Const.MAX_INJTIMEOUT:
                if not self._check_allok_2_inject(show_warn=False):
                    self._abort_injection()
                    return False
                if not self._evg_dev.injection_state:
                    break
            _time.sleep(0.02)
        else:
            # if in decay mode and autostop is turned off, interrupt wait
            while self._currinfo_dev.current < self._target_current:
                if init_mode == _Const.InjMode.Decay and \
                        init_autostop and not self._autostop:
                    return False
                _time.sleep(0.1)
            self._update_log('Target current reached!')
        return True

    def _stop_injection(self):
        # turn off injectionevt
        self._update_log('Sending turn off command to InjectionEvt...')
        if not self._evg_dev.cmd_turn_off_injection():
            self._update_log('ERR:Timed out waiting for InjectionEvt.')
            return False
        self._update_log('Turned off InjectionEvt.')

        return True

    def _update_bucket_list_autostop(self):
        old_bucklist = self._evg_dev.bucketlist_mon
        injcount = self._evg_dev.injection_count
        blistlen = self._evg_dev.bucketlist_len
        proll = int(injcount % blistlen)
        new_bucklist = _np.roll(old_bucklist, -1 * proll)
        return self._set_bucket_list(new_bucklist)

    def _update_bucket_list_topup(self):
        bucket = _np.arange(self._topupnrpulses) + 1
        bucket *= self._bucketlist_step
        bucket += self._evg_dev.bucketlist_mon[-1] - 1
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

    def _abort_injection(self):
        self._update_log('Turning off InjectionEvt...')
        if self._evg_dev.cmd_turn_off_injection():
            msg = 'Turned off InjectionEvt.'
        else:
            self._update_log('ERR:Failed to turn off InjectionEvt.')
            self._update_log('Turning off EGun TriggerPS...')
            if self._egun_dev.trigps.cmd_disable_trigger():
                msg = 'Turned off EGun TriggerPS.'
            else:
                msg = 'ERR:Failed to turn off EGun TriggerPS.'
        self._update_log(msg)

    # --- auxiliary top-up methods ---

    def _launch_topup_thread(self):
        while self._abort:
            _time.sleep(0.1)
        self._update_log('Launchig top-up thread...')
        self._topup_thread = _epics.ca.CAThread(
            target=self._do_topup, daemon=True)
        self._topup_thread.start()

    def _stop_topup_thread(self):
        if self._abort:
            return
        self._update_log('Stopping top-up thread...')
        self._abort = True
        self._topup_thread.join()
        self._topup_thread = None
        self._update_log('Stopped top-up thread.')
        self._abort = False

        # reset next injection schedule
        now = _Time.now().timestamp()
        self._topupnext = now - (now % (24*60*60)) + 3*60*60
        self.run_callbacks('TopUpNextInj-Mon', self._topupnext)

    def _do_topup(self):
        # update bucket list according to settings
        self._update_bucket_list_topup()

        # update next injection schedule
        now, period = _Time.now().timestamp(), self._topupperiod
        self._topupnext = now - (now % period) + period
        self.run_callbacks('TopUpNextInj-Mon', self._topupnext)

        # if PU standby is enabled
        if self._topuppustandbyenbl:
            if not self._update_topup_pu_refvolt():
                self._update_log('ERR:...aborted top-up loop.')
                return

            # if remaining time is short, do not handle PU voltage
            if self._topupnext - _time.time() <= _Const.PU_VOLTAGE_UP_TIME*2:
                self._topup_pu_prepared = True
            else:
                # else, set PU voltage to 50%
                self._prepare_topup('standby')

        while self._mode == _Const.InjMode.TopUp:
            if not self._check_allok_2_inject():
                break

            self._update_topupsts(_Const.TopUpSts.Waiting)
            self._update_log('Waiting for next injection...')
            if not self._wait_topup_period():
                break

            self._update_log('Top-up period elapsed. Preparing...')
            if self._currinfo_dev.current < self._target_current * 1.02:
                self._update_topupsts(_Const.TopUpSts.TurningOn)
                self._update_log('Starting injection...')
                if not self._start_injection():
                    break

                self._update_topupsts(_Const.TopUpSts.Injecting)
                self._update_log('Injecting...')
                if not self._wait_injection():
                    break

                self._update_topupsts(_Const.TopUpSts.TurningOff)
                self._update_bucket_list_topup()
            else:
                self._update_topupsts(_Const.TopUpSts.Skipping)
                self._update_log('Skipping injection...')
                _time.sleep(2)

            self._prepare_topup('standby')

            self._topupnext += self._topupperiod
            self.run_callbacks('TopUpNextInj-Mon', self._topupnext)

        self._prepare_topup('inject')

        # update top-up status
        self._update_topupsts(_Const.TopUpSts.Off)
        self._update_log('Stopped top-up loop.')
        if not self._abort:
            self._topupstate_sel = _Const.OffOn.Off
            self.run_callbacks('TopUpState-Sel', self._topupstate_sel)

    def _wait_topup_period(self):
        while _time.time() < self._topupnext:
            if not self._check_allok_2_inject(show_warn=False):
                return False
            _time.sleep(1)

            remaining = round(self._topupnext - _time.time())
            text = 'Remaining time: {}s'.format(remaining)
            self.run_callbacks('Log-Mon', text)
            if remaining % 60 == 0:
                _log.info(text)

            if remaining <= _Const.PU_VOLTAGE_UP_TIME and \
                    not self._topup_pu_prepared:
                self._prepare_topup('inject')

            if _time.time() >= self._topupnext - self._topupheadstarttime:
                return True

        self._update_log('Remaining time: 0s')
        return True

    def _prepare_topup(self, state='inject'):
        if not self._topuppustandbyenbl:
            return
        self._topup_puref_ignore = True
        if state == 'inject':
            self._topup_pu_prepared = True
            self._update_log('Setting PU Voltage to 100%...')
            for idx, dev in enumerate(self._pu_devs):
                dev.voltage = self._pu_refvolt[idx]
            self._update_log('...done.')
        elif state == 'standby':
            self._topup_pu_prepared = False
            self._update_log('Setting PU Voltage to 50%...')
            for idx, dev in enumerate(self._pu_devs):
                dev.voltage = self._pu_refvolt[idx] * 0.5
            self._update_log('...done.')
        _time.sleep(1)
        self._topup_puref_ignore = False

    def _update_topup_pu_refvolt(self):
        # get PU voltage reference
        for idx, dev in enumerate(self._pu_devs):
            spv = dev['Voltage-SP']
            if spv is None:
                self._update_topupsts(_Const.TopUpSts.Off)
                self._update_log('ERR:Could not read voltage of')
                self._update_log('ERR:'+dev.devname+'...')
                return False
            self._pu_refvolt[idx] = dev['Voltage-SP']
        return True

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
        self._topupstate_sts = sts
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
                            elif self._mode == _Const.InjMode.TopUp and \
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
            if self._mode != _Const.InjMode.TopUp:
                val = 1 if not self._evg_dev.connected else \
                    self._evg_dev.bucketlist_sync != 1
                value = _updt_bit(value, 1, val)

            if self._egun_dev.connected:
                # EGBiasPS voltage diff. from desired
                volt = self._sglbunbiasvolt \
                    if self._type == _Const.InjType.SingleBunch \
                    else self._multbunbiasvolt
                val = abs(self._egun_dev.bias.voltage - volt) > \
                    self._egun_dev.bias_voltage_tol
                value = _updt_bit(value, 2, val)

                # EGFilaPS current diff. from nominal
                val = not self._egun_dev.is_fila_on
                value = _updt_bit(value, 3, val)

                # EGHVPS voltage diff. from nominal
                val = not self._egun_dev.is_hv_on
                value = _updt_bit(value, 4, val)

                # EGPulsePS setup is diff. from desired
                val = _ETypes.INJTYPE[self._type] != \
                    _ETypes.INJTYPE_MON[self._type_mon]
                value = _updt_bit(value, 5, val)

                # EGTriggerPS is off
                val = not self._egun_dev.trigps.is_on()
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
