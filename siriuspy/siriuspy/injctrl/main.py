"""Main module of Machine Shift Application."""
import time as _time
from threading import Thread as _Thread
import logging as _log
import numpy as _np

from ..util import update_bit as _updt_bit, get_bit as _get_bit
from ..namesys import SiriusPVName as _PVName
from ..epics import PV as _PV
from ..callbacks import Callback as _Callback
from ..clientarch import Time as _Time

from ..search import PSSearch as _PSSearch, HLTimeSearch as _HLTimeSearch
from ..diagsys.lidiag.csdev import Const as _LIDiagConst
from ..diagsys.psdiag.csdev import ETypes as _PSDiagEnum
from ..diagsys.rfdiag.csdev import Const as _RFDiagConst
from ..devices import InjSysStandbyHandler, EVG, EGun, CurrInfoSI, MachShift, \
    PowerSupplyPU, RFKillBeam

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
        self._thread_type = None
        self._sglbunbiasvolt = EGun.BIAS_SINGLE_BUNCH
        self._multbunbiasvolt = EGun.BIAS_MULTI_BUNCH
        self._filaopcurr = EGun.FILACURR_OPVALUE
        self._thread_filaps = None
        self._hvopvolt = EGun.HV_OPVALUE
        self._thread_hvps = None
        self._thread_wategun = None
        self._target_current = 100.0
        self._bucketlist_start = 1
        self._bucketlist_stop = 864
        self._bucketlist_step = 15

        self._topupstate_sel = _Const.OffOn.Off
        self._topupstate_sts = _Const.TopUpSts.Off
        self._topupperiod = 15*60
        now = _Time.now().timestamp()
        self._topupnext = now - (now % (24*60*60)) + 3*60*60
        self._topupnextinjround_count = 0
        self._topupmaxnrp = 100
        self._topup_thread = None
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
        self._egun_dev = EGun(print_log=False)
        self._init_egun = False
        self._egun_dev.trigps.pv_object('enable').add_callback(
            self._callback_watch_eguntrig)
        self._egun_dev.trigps.pv_object('enablereal').add_callback(
            self._callback_autostop)

        self._evg_dev = EVG()
        self._init_injevt = False
        self._evg_dev.pv_object('InjectionEvt-Sel').add_callback(
            self._callback_watch_injectionevt)
        self._evg_dev.pv_object('InjectionEvt-Sel').add_callback(
            self._callback_autostop)
        self._evg_dev.pv_object('RepeatBucketList-RB').add_callback(
            self._callback_watch_repeatbucketlist)

        self._injsys_dev = InjSysStandbyHandler()

        self._macshift_dev = MachShift()

        self._currinfo_dev = CurrInfoSI()

        punames = _PSSearch.get_psnames(
            {'dis': 'PU', 'dev': '.*(Kckr|Sept)'})
        self._pu_devs = [PowerSupplyPU(pun) for pun in punames]

        self._rfkillbeam = RFKillBeam()

        # pvname to write method map
        self.map_pv2write = {
            'Mode-Sel': self.set_mode,
            'Type-Sel': self.set_type,
            'SglBunBiasVolt-SP': self.set_sglbunbiasvolt,
            'MultBunBiasVolt-SP': self.set_multbunbiasvolt,
            'FilaOpCurr-SP': self.set_filaopcurr,
            'HVOpVolt-SP': self.set_hvopvolt,
            'TargetCurrent-SP': self.set_target_current,
            'BucketListStart-SP': self.set_bucketlist_start,
            'BucketListStop-SP': self.set_bucketlist_stop,
            'BucketListStep-SP': self.set_bucketlist_step,
            'TopUpState-Sel': self.set_topupstate,
            'TopUpPeriod-SP': self.set_topupperiod,
            'TopUpNextInjRound-Cmd': self.cmd_nextinjround,
            'TopUpMaxNrPulses-SP': self.set_topupmaxnrp,
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
        self.thread_check_diagstatus = _Thread(
            target=self._update_diagstatus, daemon=True)
        self.thread_check_diagstatus.start()
        self.thread_check_injstatus = _Thread(
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
        self.run_callbacks('SglBunBiasVolt-SP', self._sglbunbiasvolt)
        self.run_callbacks('SglBunBiasVolt-RB', self._sglbunbiasvolt)
        self.run_callbacks('MultBunBiasVolt-SP', self._multbunbiasvolt)
        self.run_callbacks('MultBunBiasVolt-RB', self._multbunbiasvolt)
        self.run_callbacks('FilaOpCurr-SP', self._filaopcurr)
        self.run_callbacks('FilaOpCurr-RB', self._filaopcurr)
        self.run_callbacks('HVOpVolt-SP', self._hvopvolt)
        self.run_callbacks('HVOpVolt-RB', self._hvopvolt)
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
        self.run_callbacks('TopUpPeriod-SP', self._topupperiod)
        self.run_callbacks('TopUpPeriod-RB', self._topupperiod)
        self.run_callbacks('TopUpNextInj-Mon', self._topupnext)
        self.run_callbacks(
            'TopUpNextInjRound-Cmd', self._topupnextinjround_count)
        self.run_callbacks('TopUpMaxNrPulses-SP', self._topupmaxnrp)
        self.run_callbacks('TopUpMaxNrPulses-RB', self._topupmaxnrp)
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
            self._update_log('Waiting to start top-up.')
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
        self._type = value
        self.run_callbacks('Type-Sts', self._type)

        target = self._egun_dev.cmd_switch_to_single_bunch \
            if value == _Const.InjType.SingleBunch else \
            self._egun_dev.cmd_switch_to_multi_bunch
        self._thread_type = _Thread(target=target, daemon=True)
        self._thread_type.start()

        if self._thread_wategun is None or not self._thread_wategun.is_alive():
            self._thread_wategun = _Thread(
                target=self._watch_egundev, daemon=True)
            self._thread_wategun.start()
        return True

    def set_sglbunbiasvolt(self, value):
        """Set single bunch bias voltage."""
        self._update_log('Received setpoint to SB Bias voltage.')
        self._egun_dev.single_bunch_bias_voltage = value
        self._sglbunbiasvolt = value
        self.run_callbacks('SglBunBiasVolt-RB', self._sglbunbiasvolt)

        if self._type == _Const.InjType.SingleBunch:
            _Thread(target=self._set_egunbias,
                    args=[value, ], daemon=True).start()
        return True

    def set_multbunbiasvolt(self, value):
        """Set multi bunch bias voltage."""
        self._update_log('Received setpoint to MB Bias voltage.')
        self._egun_dev.multi_bunch_bias_voltage = value
        self._multbunbiasvolt = value
        self.run_callbacks('MultBunBiasVolt-RB', self._multbunbiasvolt)

        if self._type == _Const.InjType.MultiBunch:
            _Thread(target=self._set_egunbias,
                    args=[value, ], daemon=True).start()
        return True

    def _set_egunbias(self, value):
        self._update_log('Setting EGun Bias voltage to {}V...'.format(value))
        if not self._egun_dev.bias.set_voltage(value):
            self._update_log('ERR:Could not set EGun Bias voltage.')
        else:
            self._update_log('Set EGun Bias voltage: {}V.'.format(value))

    def set_filaopcurr(self, value):
        """Set filament current operation value."""
        self._egun_dev.fila_current_opvalue = value
        self._filaopcurr = value
        self.run_callbacks('FilaOpCurr-RB', self._filaopcurr)

        self._thread_filaps = _Thread(
            target=self._egun_dev.set_fila_current, daemon=True)
        self._thread_filaps.start()

        if self._thread_wategun is None or not self._thread_wategun.is_alive():
            self._thread_wategun = _Thread(
                target=self._watch_egundev, daemon=True)
            self._thread_wategun.start()
        return True

    def set_hvopvolt(self, value):
        """Set high voltage operation value."""
        self._egun_dev.high_voltage_opvalue = value
        self._hvopvolt = value
        self.run_callbacks('HVOpVolt-RB', self._hvopvolt)

        self._thread_hvps = _Thread(
            target=self._egun_dev.set_hv_voltage, daemon=True)
        self._thread_hvps.start()

        if self._thread_wategun is None or not self._thread_wategun.is_alive():
            self._thread_wategun = _Thread(
                target=self._watch_egundev, daemon=True)
            self._thread_wategun.start()
        return True

    def _watch_egundev(self):
        running = True
        sts = ''
        while running:
            filarun = self._thread_filaps is not None and \
                self._thread_filaps.is_alive()
            hvpsrun = self._thread_hvps is not None and \
                self._thread_hvps.is_alive()
            typerun = self._thread_type is not None and \
                self._thread_type.is_alive()
            running = filarun | hvpsrun | typerun
            if self._egun_dev.last_status != sts:
                sts = self._egun_dev.last_status
                if 'err:' in sts.lower():
                    sts = sts.split(':')[1]
                    msgs = ['ERR:'+sts[i:i+35] for i in range(0, len(sts), 35)]
                else:
                    msgs = [sts[i:i+39] for i in range(0, len(sts), 39)]
                for msg in msgs:
                    self._update_log(msg)
            _time.sleep(0.05)

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
            if self._topup_thread and not self._topup_thread.is_alive()\
                    or not self._topup_thread:
                self._topupnext = _Time.now().timestamp()
                self.run_callbacks('TopUpNextInj-Mon', self._topupnext)
                self._launch_topup_thread()
        else:
            self._update_log('Stop received!')
            if self._topup_thread and self._topup_thread.is_alive():
                self._stop_topup_thread()
                now = _Time.now().timestamp()
                self._topupnext = now - (now % (24*60*60)) + 3*60*60
                self.run_callbacks('TopUpNextInj-Mon', self._topupnext)

        return True

    def set_topupperiod(self, value):
        """Set top-up period."""
        if not 30 <= value <= 6*60*60:
            return False

        if self._topupstate_sts != _Const.TopUpSts.Off:
            self._topupnext = self._topupnext - self._topupperiod + value
            self.run_callbacks('TopUpNextInj-Mon', self._topupnext)

        self._topupperiod = value
        self._update_log('Changed top-up period to '+str(value)+'s.')
        self.run_callbacks('TopUpPeriod-RB', self._topupperiod)
        return True

    def set_topupmaxnrp(self, value):
        """Set top-up maximum number of injection pulses."""
        if not 1 <= value <= 1000:
            return False

        self._topupmaxnrp = value
        self._update_log('Changed top-up max.nr.pulses to '+str(value)+'.')
        self.run_callbacks('TopUpMaxNrPulses-RB', self._topupmaxnrp)
        return True

    def cmd_nextinjround(self, value):
        """Round next injection time instant to smallest minute nearest."""
        nextinj = self._topupnext
        self._topupnext = nextinj - (nextinj % 60)
        self.run_callbacks('TopUpNextInj-Mon', self._topupnext)

        self._topupnextinjround_count += 1
        self.run_callbacks(
            'TopUpNextInjRound-Cmd', self._topupnextinjround_count)
        return False

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

    def cmd_injsys_turn_on(self, value):
        """Set turn on Injection System."""
        run = self._injsys_dev.is_running
        if run:
            self._update_log('ERR:Still processing turn '+run+' InjSystem')
            return False

        self._update_log('Sending turn on to Inj.System...')
        self.run_callbacks(
            'InjSysCmdDone-Mon', ','.join(self._injsys_dev.done))
        self._injsys_dev.cmd_turn_on(run_in_thread=True)
        _Thread(target=self._watch_injsys, args=['on', ], daemon=True).start()

        self._injsys_turn_on_count += 1
        self.run_callbacks('InjSysTurnOn-Cmd', self._injsys_turn_on_count)
        return False

    def cmd_injsys_turn_off(self, value):
        """Set turn off Injection System."""
        run = self._injsys_dev.is_running
        if run:
            self._update_log('ERR:Still processing turn '+run+' InjSystem')
            return False

        self._update_log('Sending turn off to Inj.System...')
        self.run_callbacks(
            'InjSysCmdDone-Mon', ','.join(self._injsys_dev.done))
        self._injsys_dev.cmd_turn_off(run_in_thread=True)
        _Thread(target=self._watch_injsys, args=['off', ], daemon=True).start()

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
        _Thread(target=self._watch_rfkillbeam, daemon=True).start()

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
        _Thread(target=self._watch_eguntrig,
                args=[value, ], daemon=True).start()

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
        _Thread(target=self._watch_injti, args=[value, ], daemon=True).start()

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

        _Thread(target=self._run_autostop, daemon=True).start()

    def _run_autostop(self):
        self._update_log('Injection Auto Stop activated...')
        if not self._wait_autostop():
            self._update_log('Injection Auto Stop Routine aborted.')
            return

        if self._stop_injection():
            self._update_log('Injection Auto Stop done.')
            self._update_bucket_list()
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

    def _callback_watch_repeatbucketlist(self, value, **kws):
        if self._mode == _Const.InjMode.TopUp:
            return
        if self._autostop == _Const.OffOn.On and value != 0:
            self._autostop = _Const.OffOn.Off
            self.run_callbacks('AutoStop-Sel', self._autostop)
            self.run_callbacks('AutoStop-Sts', self._autostop)
            self._update_log('WARN:RepeatBucketList is diff. from 0.')
            self._update_log('WARN:Turned Off Auto Stop.')

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
            if self._evg_dev.nrpulses != 0:
                self._update_log('ERR:Aborted. Set RepeatBucketList to 0.')
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

        # turn on PU Pulse
        self._update_log('Turning on PU Pulse...')
        for pudev in self._pu_devs:
            pudev.pulse = _Const.DsblEnbl.Enbl
            _time.sleep(0.5)
        _t0 = _time.time()
        while _time.time() - _t0 < 3:
            if all([pud.pulse == _Const.DsblEnbl.Enbl
                    for pud in self._pu_devs]):
                self._update_log('Turned on PU Pulse.')
                break
        else:
            self._update_log('ERR:Timed out waiting for PU to be on.')
            return False

        # wait for injectionevt to be ready
        self._update_log('Waiting for InjectionEvt to be on...')
        _t0 = _time.time()
        while _time.time() - _t0 < _Const.TI_INJ_TIMEOUT:
            if not self._check_allok_2_inject(show_warn=False):
                self._abort_injection()
                return False
            if self._evg_dev.injection_state:
                break
            _time.sleep(0.1)
        else:
            self._update_log('ERR:Timed out waiting for InjectionEvt.')
            return False

        self._update_log('InjectionEvt is on!')
        return True

    def _wait_injection(self):
        init_mode = self._mode
        init_autostop = self._autostop
        while self._currinfo_dev.current < self._target_current:
            # if there are problems, abort injection
            if not self._check_allok_2_inject(show_warn=False):
                self._abort_injection()
                return False
            # if in decay mode and autostop is turned off, interrupt wait
            if init_mode == _Const.InjMode.Decay and \
                    init_autostop and not self._autostop:
                return False
            # if in TopUp mode and max pulses exceeded, stop injection
            if self._mode == _Const.InjMode.TopUp and \
                    self._evg_dev.injection_count >= self._topupmaxnrp:
                self._update_log('ERR:Max.Nr.Pulses exceeded. Stopping.')
                self._abort_injection()
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

        if self._mode == _Const.InjMode.Decay:
            return True

        # turn off PU Pulse
        self._update_log('Turning off PU Pulse...')
        for pudev in self._pu_devs:
            pudev.pulse = _Const.DsblEnbl.Dsbl
            _time.sleep(0.5)
        _t0 = _time.time()
        while _time.time() - _t0 < 3:
            if all([pud.pulse == _Const.DsblEnbl.Dsbl
                    for pud in self._pu_devs]):
                self._update_log('Turned off PU Pulse.')
                return True
        self._update_log('ERR:Timed out waiting for PU to be off.')
        return False

    def _update_bucket_list(self):
        old_bucklist = self._evg_dev.bucketlist_mon
        injcount = self._evg_dev.injection_count
        blistlen = self._evg_dev.bucketlist_len
        proll = int(injcount % blistlen)
        new_bucklist = _np.roll(old_bucklist, -1 * proll)
        self._evg_dev.bucketlist = new_bucklist
        if not _np.all(self._evg_dev.bucketlist == new_bucklist):
            self._update_log('WARN:Could not update BucketList.')
        else:
            self._update_log('Updated BucketList.')

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
        self._topup_thread = _Thread(target=self._do_topup, daemon=True)
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

    def _do_topup(self):
        while self._mode == _Const.InjMode.TopUp:
            if not self._check_allok_2_inject():
                break

            self._topupnext += self._topupperiod
            self.run_callbacks('TopUpNextInj-Mon', self._topupnext)

            if self._currinfo_dev.current <= self._target_current:
                self._update_topupsts(_Const.TopUpSts.TurningOn)
                self._update_log('Starting injection...')
                if not self._start_injection():
                    break

                self._update_topupsts(_Const.TopUpSts.Injecting)
                self._update_log('Injecting...')
                if not self._wait_injection():
                    break

                self._update_topupsts(_Const.TopUpSts.TurningOff)
                self._update_log('Stopping injection...')
                if not self._stop_injection():
                    break
                self._update_bucket_list()

            self._update_topupsts(_Const.TopUpSts.Waiting)
            self._update_log('Waiting for next injection...')

            if not self._wait_topup_period():
                break
            self._update_log('Top-up period elapsed. Preparing...')

        self._update_topupsts(_Const.TopUpSts.Off)
        self._update_log('Stopped top-up loop.')
        if not self._abort:
            self._topupstate_sel = _Const.OffOn.Off
            self.run_callbacks('TopUpState-Sel', self._topupstate_sel)

    def _wait_topup_period(self):
        _t0 = _time.time()
        while _time.time() < self._topupnext:
            if not self._check_allok_2_inject(show_warn=False):
                return False
            _time.sleep(1)

            elapsed = int(_time.time() - _t0)
            remaining = int(self._topupnext - _time.time())
            text = 'Remaining time: {}s'.format(remaining)
            self.run_callbacks('Log-Mon', text)
            if elapsed % 60 == 0:
                _log.info(text)

            if self._currinfo_dev.current < self._target_current and \
                    _time.time() > self._topupnext - self._get_adv_estim():
                return True

        self._update_log('Remaining time: 0s')
        return True

    def _get_adv_estim(self):
        return 0 if self._evg_dev.bucketlist_len is None \
            else self._evg_dev.bucketlist_len

    # --- auxiliary log methods ---

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
        tplanned = 1.0/App.SCAN_FREQUENCY
        psdiag = _PSDiagEnum.DIAG_STATUS_LABELS_AS
        psalrm = int(1 << len(psdiag)) - 1 - int(1 << psdiag.index('Alarms'))
        while not self.quit:
            if not self.scanning:
                _time.sleep(tplanned)
                continue

            _t0 = _time.time()

            # update sections status
            self._status_problems = set()
            for sec, sub2pvs in self._pvs_diag.items():
                lbls = _get_sts_lbls(sec)
                for sub, d2pv in sub2pvs.items():
                    if sub not in lbls:
                        continue
                    bit = lbls.index(sub)
                    problems = set()
                    for pvo in d2pv.values():
                        if pvo.connected:
                            if sub == 'PS':  # disregard alarms
                                value = _np.bitwise_and(int(pvo.value), psalrm)
                                nok = value > 0
                            else:
                                nok = pvo.value > 0
                        else:
                            nok = True
                        if nok:
                            problems.add(_PVName(pvo.pvname).device_name)
                    val = 1 if problems else 0
                    self._status[sec] = _updt_bit(self._status[sec], bit, val)
                    if len(problems) > 1:
                        self._status_problems.add(sec+' '+sub)
                    else:
                        self._status_problems.update(problems)
                self.run_callbacks('DiagStatus'+sec+'-Mon', self._status[sec])

            # compile general status
            lbls = _get_sts_lbls()
            for bit, sec in enumerate(lbls):
                val = self._status[sec] != 0
                self._status['All'] = _updt_bit(self._status['All'], bit, val)
            self.run_callbacks('DiagStatus-Mon', self._status['All'])

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
