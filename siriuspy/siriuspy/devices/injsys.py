"""InjSys Standby Handler devices."""

import time as _time
from copy import deepcopy as _dcopy
from threading import Thread as _Thread, Event as _Flag
import logging as _log

from .device import Devices as _Devices, DeviceNC as _DeviceNC
from .lillrf import DevLILLRF
from .modltr import LIModltr
from .pwrsupply import PowerSupply, PowerSupplyPU
from .timing import EVG, Event, Trigger
from .rf import ASLLRF
from .posang import PosAng

from ..search import PSSearch, HLTimeSearch
from ..csdev import Const as _Const
from ..timesys.csdev import Const as _TIConst
from ..pwrsupply.csdev import Const as _PSConst
from ..callbacks import Callback as _Callback


class _BaseHandler(_Devices):
    """Base standby mode handler for injection procedure."""

    @property
    def is_on(self):
        """Is on."""
        for dev, ppties in self._on_values.items():
            for ppty, val in ppties.items():
                if not dev[ppty] == val:
                    return False
        return True

    @property
    def on_values(self):
        """Property values equivalent to 'on' status."""
        vals = dict()
        for dev, ppties in self._on_values.items():
            for ppty, val in ppties.items():
                vals[dev.pv_object(ppty).pvname] = val
        return vals


class ASPUStandbyHandler(_BaseHandler):
    """Pulsed magnets standby mode handler for injection procedure."""

    def __init__(self):
        """Init."""
        self._punames = PSSearch.get_psnames(
            {'dis': 'PU', 'dev': '.*(Kckr|Sept)'})
        self._trignames = [
            dev.replace('PU', 'TI') for dev in self._punames]
        self._modnames = LIModltr.DEVICES.ALL

        # pu devices
        self._pudevs = [PowerSupplyPU(pun) for pun in self._punames]

        # trigger devices
        self._trigdevs = [Trigger(trg) for trg in self._trignames]

        # modulator devices
        self._moddevs = [LIModltr(mod) for mod in self._modnames]
        self._limps = _DeviceNC(
            'LA-CN:H1MPS-1',
            ('Mod1State_I', 'Mod1State_L', 'Mod1State_R',
             'Mod2State_I', 'Mod2State_L', 'Mod2State_R'))

        alldevs = self._pudevs + self._trigdevs + self._moddevs
        alldevs.append(self._limps)
        alldevs = tuple(alldevs)

        self._on_values = dict()
        for pudev in self._pudevs:
            if 'InjDpKckr' in pudev.devname:
                continue
            self._on_values[pudev] = {
                'Pulse-Sts': _PSConst.DsblEnbl.Enbl,
                'PwrState-Sts': _PSConst.DsblEnbl.Enbl}
        for tdev in self._trigdevs:
            if 'InjDpKckr' in tdev.devname:
                continue
            self._on_values[tdev] = {
                'State-Sts': _TIConst.DsblEnbl.Enbl}
        for mdev in self._moddevs:
            self._on_values[mdev] = {
                'CHARGE': _TIConst.DsblEnbl.Enbl,
                'TRIGOUT': _TIConst.DsblEnbl.Enbl,
                'TRIG_Norm': 1,
                'Pulse_Current': 1,
                'CPS_ALL': 1,
            }
        self._on_values[self._limps] = {
            'Mod1State_I': 0,
            'Mod1State_L': 0,
            'Mod2State_I': 0,
            'Mod2State_L': 0,
        }

        # call base class constructor
        super().__init__('', alldevs)

    @property
    def punames(self):
        """Power supply names."""
        return _dcopy(self._punames)

    @property
    def pudevices(self):
        """Power supply devices."""
        return self._pudevs

    @property
    def trignames(self):
        """Trigger names."""
        return _dcopy(self._trignames)

    @property
    def trigdevices(self):
        """Trigger devices."""
        return self._trigdevs

    @property
    def modnames(self):
        """Modulator names."""
        return _dcopy(self._modnames)

    @property
    def moddevices(self):
        """Modulator devices."""
        return self._moddevs

    def cmd_turn_off(self):
        """Turn off."""
        # turn modulator trigout off
        self._set_devices_propty(
            self._moddevs, 'TRIGOUT', _Const.DsblEnbl.Dsbl)

        # wait for modulator trigout to turn off
        retval = self._wait_devices_propty(
            self._moddevs, 'TRIGOUT', _Const.DsblEnbl.Dsbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for LI modulator TrigOut to be off timed '\
                   'out without success! Verify LI Modulators!'
            return [False, text, retval[1]]

        # set pulsed magnet pulse off
        self._set_devices_propty(
            self._pudevs, 'Pulse-Sel', _PSConst.DsblEnbl.Dsbl)

        # wait for pulsed magnet pulse to be off
        retval = self._wait_devices_propty(
            self._pudevs, 'Pulse-Sts', _PSConst.DsblEnbl.Dsbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for pulsed magnet Pulse to be disabled '\
                   'timed out without success! Verify pulsed magnets!'
            return [False, text, retval[1]]

        # set pulsed magnet power state off
        self._set_devices_propty(
            self._pudevs, 'PwrState-Sel', _PSConst.DsblEnbl.Dsbl)

        # wait for pulsed magnet power state to be off
        retval = self._wait_devices_propty(
            self._pudevs, 'PwrState-Sts', _PSConst.DsblEnbl.Dsbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for pulsed magnet PwrState to be off '\
                   'timed out without success! Verify pulsed magnets!'
            return [False, text, retval[1]]

        # wait for modulators trig.out
        _time.sleep(1)

        # turn modulator charge off
        self._set_devices_propty(
            self._moddevs, 'CHARGE', _Const.DsblEnbl.Dsbl)

        # wait for modulator charge to turn off
        retval = self._wait_devices_propty(
            self._moddevs, 'CHARGE', _Const.DsblEnbl.Dsbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for LI modulator Charge to be off timed '\
                   'out without success! Verify LI Modulators!'
            return [False, text, retval[1]]

        return True, '', []

    def cmd_turn_on(self):
        """Turn on."""
        # turn modulators charge on
        self._set_devices_propty(
            self._moddevs, 'CHARGE', _Const.DsblEnbl.Enbl)

        # wait for modulators charge to turn on
        retval = self._wait_devices_propty(
            self._moddevs, 'CHARGE', _Const.DsblEnbl.Enbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for LI modulator Charge to be on timed '\
                   'out without success! Verify LI Modulators!'
            return [False, text, retval[1]]

        # reset modulator
        for dev in self._moddevs:
            if not dev.cmd_reset():
                text = 'Could not reset LI modulator! Verify LI Modulators!'
                return [False, text, [dev.devname+':RESET', ]]

        devs = [dev for dev in self._pudevs if 'InjDpKckr' not in dev.devname]

        # set pulsed magnet power state on
        self._set_devices_propty(devs, 'PwrState-Sel', _PSConst.DsblEnbl.Enbl)

        # wait for pulsed magnet power state to be on
        retval = self._wait_devices_propty(
            devs, 'PwrState-Sts', _PSConst.DsblEnbl.Enbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for pulsed magnet PwrState to be on '\
                   'timed out without success! Verify pulsed magnets!'
            return [False, text, retval[1]]

        # wait a moment for the PU high voltage and modulators charge
        _time.sleep(1)

        # set pulsed magnet pulse on
        self._set_devices_propty(devs, 'Pulse-Sel', _PSConst.DsblEnbl.Enbl)

        # wait for pulsed magnet pulse to be on
        retval = self._wait_devices_propty(
            devs, 'Pulse-Sts', _PSConst.DsblEnbl.Enbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for pulsed magnet Pulse to be enabled '\
                   'timed out without success! Verify pulsed magnets!'
            return [False, text, retval[1]]

        # turn modulator trigout on
        self._set_devices_propty(
            self._moddevs, 'TRIGOUT', _Const.DsblEnbl.Enbl)

        # wait for modulator trigout to turn on
        retval = self._wait_devices_propty(
            self._moddevs, 'TRIGOUT', _Const.DsblEnbl.Enbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for LI modulator TrigOut to be on timed '\
                   'out without success! Verify LI Modulators!'
            return [False, text, retval[1]]

        # check if mps status is ok
        _t0 = _time.time()
        while _time.time() - _t0 < 5:
            if not self._limps['Mod1State_I'] and \
                    not self._limps['Mod2State_I']:
                break
        else:
            problems = [
                self._limps.pv_object('Mod'+i+'State_I').pvname for
                i in ['1', '2'] if self._limps['Mod'+i+'State_I']]
            text = 'Check for LI modulators MPS Status to be ok timed '\
                   'out without success! Verify LI Modulators MPS!'
            return [False, text, problems]

        # reset linac mps modulator signal
        self._limps['Mod1State_R'] = 1
        self._limps['Mod2State_R'] = 1
        _time.sleep(1)
        self._limps['Mod1State_R'] = 0
        self._limps['Mod2State_R'] = 0

        # check if mps latch is ok
        _t0 = _time.time()
        while _time.time() - _t0 < 5:
            if not self._limps['Mod1State_L'] and \
                    not self._limps['Mod2State_L']:
                break
        else:
            problems = [
                self._limps.pv_object('Mod'+i+'State_L').pvname for
                i in ['1', '2'] if self._limps['Mod'+i+'State_L']]
            text = 'Check for LI modulators MPS Latch to be ok timed '\
                   'out without success! Verify LI Modulators MPS!'
            return [False, text, problems]

        return True, '', []


class BOPSRampStandbyHandler(_BaseHandler):
    """BO PS Ramp standy mode handler for injection procedure."""

    def __init__(self):
        """Init."""
        self._psnames = PSSearch.get_psnames(
            {'sec': 'BO', 'dis': 'PS'})
        self._trignames = HLTimeSearch.get_hl_triggers(
            {'sec': 'BO', 'dev': 'Mags'})

        # ps devices
        self._psdevs = [PowerSupply(psn) for psn in self._psnames]

        # trigger devices
        self._trigdevs = [Trigger(trg) for trg in self._trignames]

        alldevs = tuple(self._psdevs + self._trigdevs)

        self._on_values = dict()
        for psdev in self._psdevs:
            self._on_values[psdev] = {
                'OpMode-Sts': _PSConst.States.RmpWfm,
                'WfmUpdateAuto-Sts': _PSConst.DsblEnbl.Enbl}
        for tdev in self._trigdevs:
            self._on_values[tdev] = {
                'State-Sts': _TIConst.DsblEnbl.Enbl,
                'Src-Sts': tdev.source_options.index('RmpBO')}

        # call base class constructor
        super().__init__('', alldevs)

    @property
    def psnames(self):
        """Power supply names."""
        return _dcopy(self._psnames)

    @property
    def psdevices(self):
        """Power supply devices."""
        return self._psdevs

    @property
    def trignames(self):
        """Trigger names."""
        return _dcopy(self._trignames)

    @property
    def trigdevices(self):
        """Trigger devices."""
        return self._trigdevs

    def cmd_turn_off(self):
        """Turn off."""
        # disable triggers
        self._set_devices_propty(
            self._trigdevs, 'State-Sel', _TIConst.DsblEnbl.Dsbl)

        # wait for triggers to be disabled
        retval = self._wait_devices_propty(
            self._trigdevs, 'State-Sts', _TIConst.DsblEnbl.Dsbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for BO Mags Triggers to be disabled timed '\
                   'out without success! Verify BO Mags Triggers!'
            return [False, text, retval[1]]

        # wait duration of a ramp for PS change opmode
        _time.sleep(0.5)

        # set slowref
        self._set_devices_propty(
            self._psdevs, 'OpMode-Sel', _PSConst.OpMode.SlowRef)

        # wait for PS change opmode
        retval = self._wait_devices_propty(
            self._psdevs, 'OpMode-Sts', _PSConst.States.SlowRef,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for BO PS to be in OpMode SlowRef '\
                   'timed out without success! Verify BO PS!'
            return [False, text, retval[1]]

        # set current to zero
        self._set_devices_propty(self._psdevs, 'Current-SP', 0.0)

        # wait current change to zero
        retval = self._wait_devices_propty(
            self._psdevs, 'Current-RB', 0.0,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for BO PS to be with current zero '\
                   'timed out without success! Verify BO PS!'
            return [False, text, retval[1]]

        return True, '', []

    def cmd_turn_on(self):
        """Turn on."""
        # set rmpwfm
        self._set_devices_propty(
            self._psdevs, 'OpMode-Sel', _PSConst.OpMode.RmpWfm)

        # wait for PS change opmode
        retval = self._wait_devices_propty(
            self._psdevs, 'OpMode-Sts', _PSConst.States.RmpWfm,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for BO PS to be in OpMode RmpWfm '\
                   'timed out without success! Verify BO PS!'
            return [False, text, retval[1]]

        # set WfmUpdateAuto
        self._set_devices_propty(
            self._psdevs, 'WfmUpdateAuto-Sel', _PSConst.DsblEnbl.Enbl)

        # wait for PS WfmUpdateAuto to be enabled
        retval = self._wait_devices_propty(
            self._psdevs, 'WfmUpdateAuto-Sts', _PSConst.DsblEnbl.Enbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for BO PS WfmUpdateAuto to be enable '\
                   'timed out without success! Verify BO PS!'
            return [False, text, retval[1]]

        # configure trigger source
        values = [dev.source_options.index('RmpBO') for dev in self._trigdevs]
        self._set_devices_propty(self._trigdevs, 'Src-Sel', values)

        # wait for trigger source to be configured
        retval = self._wait_devices_propty(
            self._trigdevs, 'Src-Sts', values, timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for BO Mags Triggers to be in RmpBO event '\
                   'timed out without success! Verify BO Mags Triggers!'
            return [False, text, retval[1]]

        # enable triggers
        self._set_devices_propty(
            self._trigdevs, 'State-Sel', _TIConst.DsblEnbl.Enbl)

        # wait for triggers to be enable
        retval = self._wait_devices_propty(
            self._trigdevs, 'State-Sts', _TIConst.DsblEnbl.Enbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for BO Mags Triggers to be enable timed '\
                   'out without success! Verify BO Mags Triggers!'
            return [False, text, retval[1]]

        return True, '', []


class BORFRampStandbyHandler(_BaseHandler):
    """BO RF Ramp standby mode handler for injection procedure."""

    def __init__(self):
        self.llrf = ASLLRF(ASLLRF.DEVICES.BO)
        self.rmptrg = Trigger('BO-Glob:TI-LLRF-Rmp')

        devices = (self.llrf, self.rmptrg)

        self._on_values = dict()
        self._on_values[self.llrf] = {
            'RmpEnbl-Sts': _Const.DsblEnbl.Enbl,
            'RmpReady-Mon': _Const.DsblEnbl.Enbl}
        self._on_values[self.rmptrg] = {
            'State-Sts': _Const.DsblEnbl.Enbl}

        # call base class constructor
        super().__init__('', devices)

    def cmd_turn_off(self):
        """Turn off."""
        # set RF ramp to disable
        self.llrf.rmp_enable = _Const.DsblEnbl.Dsbl

        # wait for RF ramp to be disable
        retval = self._wait_devices_propty(
            self.llrf, 'RmpEnbl-Sts', _Const.DsblEnbl.Dsbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for BO RF Ramp to be disabled timed '\
                   'out without success! Verify BO RF Ramp!'
            return [False, text, retval[1]]

        return True, '', []

    def cmd_turn_on(self):
        """Turn on."""
        # set RF ramp to enabled
        self.llrf.rmp_enable = _Const.DsblEnbl.Enbl

        # wait for RF ramp to be enabled
        retval = self._wait_devices_propty(
            self.llrf, 'RmpEnbl-Sts', _Const.DsblEnbl.Enbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for BO RF Ramp to be enabled timed '\
                   'out without success! Verify BO RF Ramp!'
            return [False, text, retval[1]]

        return True, '', []


class InjBOStandbyHandler(_BaseHandler):
    """InjBO Event standby mode handler for injection procedure."""

    def __init__(self):
        self.evg = EVG()
        self.injboevt = Event('InjBO')

        devices = (self.evg, self.injboevt)

        self._on_values = {
            self.injboevt: {'Mode-Sts': Event.MODES.index('Continuous')}}

        # call base class constructor
        super().__init__('', devices)

    def cmd_turn_off(self):
        """Turn off."""
        # disable injbo
        self.injboevt.mode = 'Disable'

        # wait for injbo to be disabled
        retval = self._wait_devices_propty(
            self.injboevt, 'Mode-Sts', Event.MODES.index('Disable'),
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for InjBO Event to be disabled timed '\
                   'out without success! Verify InjBO Event!'
            return [False, text, retval[1]]

        # update events
        _time.sleep(1)
        self.evg.cmd_update_events()
        _time.sleep(1)

        return True, '', []

    def cmd_turn_on(self):
        """Turn on."""
        # set injbo to Continuous table
        self.injboevt.mode = 'Continuous'

        # wait for injbo to be in Continuous Table
        retval = self._wait_devices_propty(
            self.injboevt, 'Mode-Sts', Event.MODES.index('Continuous'),
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for InjBO Event to be in Continuous table '\
                   'timed out without success! Verify InjBO Event!'
            return [False, text, retval[1]]

        # update events
        self.evg.cmd_update_events()

        return True, '', []


class LILLRFStandbyHandler(_BaseHandler):
    """LI LLRF standby mode handler for injection procedure."""

    WAIT_2_TURNON = 2  # [s]

    def __init__(self):
        """Init."""

        # create devices
        devices = list()
        for dev in DevLILLRF.DEVICES.ALL:
            devices.append(DevLILLRF(dev))
        devices = tuple(devices)

        self._on_values = dict()
        for dev in devices:
            self._on_values[dev] = {
                'GET_INTEGRAL_ENABLE': _Const.DsblEnbl.Enbl,
                'GET_FB_MODE': _Const.DsblEnbl.Enbl}

        # call base class constructor
        super().__init__('', devices)

    def cmd_turn_off(self):
        """Turn off."""
        # turn feedback off
        self._set_devices_propty(
            self.devices, 'SET_FB_MODE', _Const.DsblEnbl.Dsbl)

        # wait for feedback to turn off
        retval = self._wait_devices_propty(
            self.devices, 'GET_FB_MODE', _Const.DsblEnbl.Dsbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for LI LLRF Feedback Mode to be off '\
                   'timed out without success! Verify LI LLRF!'
            return [False, text, retval[1]]

        # turn integral off
        self._set_devices_propty(
            self.devices, 'SET_INTEGRAL_ENABLE', _Const.DsblEnbl.Dsbl)

        # wait for integral to turn off
        retval = self._wait_devices_propty(
            self.devices, 'GET_INTEGRAL_ENABLE', _Const.DsblEnbl.Dsbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for LI LLRF Integral Mode to be off '\
                   'timed out without success! Verify LI LLRF!'
            return [False, text, retval[1]]

        return True, '', []

    def cmd_turn_on(self):
        """Turn on."""
        # wait for some InjBO pulses
        _time.sleep(LILLRFStandbyHandler.WAIT_2_TURNON)

        # turn integral on
        self._set_devices_propty(
            self.devices, 'SET_INTEGRAL_ENABLE', _Const.DsblEnbl.Enbl)

        # wait for integral to turn on
        retval = self._wait_devices_propty(
            self.devices, 'GET_INTEGRAL_ENABLE', _Const.DsblEnbl.Enbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for LI LLRF Integral Mode to be on '\
                   'timed out without success! Verify LI LLRF!'
            return [False, text, retval[1]]

        # turn feedback on
        self._set_devices_propty(
            self.devices, 'SET_FB_MODE', _Const.DsblEnbl.Enbl)

        # wait for feedback to turn on
        retval = self._wait_devices_propty(
            self.devices, 'GET_FB_MODE', _Const.DsblEnbl.Enbl,
            timeout=3, return_prob=True)
        if not retval[0]:
            text = 'Check for LI LLRF Feedback Mode to be on '\
                   'timed out without success! Verify LI LLRF!'
            return [False, text, retval[1]]

        return True, '', []


class InjSysStandbyHandler(_Devices):
    """Injection system standy mode handler."""

    DEF_ON_ORDER = ['bo_rf', 'as_pu', 'bo_ps', 'injbo', 'li_rf']
    DEF_OFF_ORDER = ['bo_rf', 'li_rf', 'injbo', 'as_pu', 'bo_ps']
    HANDLER_DESC = {
        'as_pu': 'AS PU (Septa, Kickers and Modulators)',
        'bo_ps': 'BO PS Ramp',
        'bo_rf': 'BO RF Ramp',
        'injbo': 'TI InjBO Event',
        'li_rf': 'LI LLRF (Klystrons Loop)',
    }

    def __init__(self):
        """Init."""
        devs = {
            'as_pu': ASPUStandbyHandler(),
            'bo_ps': BOPSRampStandbyHandler(),
            'bo_rf': BORFRampStandbyHandler(),
            'injbo': InjBOStandbyHandler(),
            'li_rf': LILLRFStandbyHandler(),
        }
        self._dev_refs = devs
        self._on_order = InjSysStandbyHandler.DEF_ON_ORDER
        self._off_order = InjSysStandbyHandler.DEF_OFF_ORDER
        self._is_running = ''
        self._done = list()
        self._result = None
        self._thread = None
        self._abort = False

        self._on_values = dict()
        for dev in devs.values():
            self._on_values.update(dev.on_values)

        # call super init
        super().__init__('', tuple(devs.values()))

    @property
    def on_order(self):
        """On setpoints order."""
        return _dcopy(self._on_order)

    @on_order.setter
    def on_order(self, value):
        self._on_order = value

    @property
    def off_order(self):
        """Off setpoints order."""
        return _dcopy(self._off_order)

    @off_order.setter
    def off_order(self, value):
        self._off_order = value

    @property
    def is_on(self):
        """Is on."""
        for dev in self.devices:
            if not dev.is_on:
                return False
        return True

    @property
    def on_values(self):
        """Dict with PVs to be monitored and their respective 'on' value."""
        return self._on_values

    @property
    def is_running(self):
        """Is running."""
        return self._is_running

    @property
    def done(self):
        """Return commands already done."""
        return self._done

    @property
    def result(self):
        """Command result."""
        return self._result

    def cmd_abort(self):
        """Abort command."""
        if self._is_running:
            self._abort = True
        return True

    def cmd_reset_comm_order(self):
        """Reset commands order."""
        self.on_order = InjSysStandbyHandler.DEF_ON_ORDER
        self.off_order = InjSysStandbyHandler.DEF_OFF_ORDER
        return True

    def cmd_turn_on(self, run_in_thread=False):
        """Turn on."""
        return self._command_base('on', run_in_thread)

    def cmd_turn_off(self, run_in_thread=False):
        """Turn off."""
        return self._command_base('off', run_in_thread)

    # --- private methods ---

    def _command_base(self, cmmtype, run_in_thread):
        if self.is_running:
            _log.error('Commands already running!')
            return

        if run_in_thread:
            self._is_running = cmmtype
            self._thread = _Thread(
                target=self._command_target, args=[cmmtype, ], daemon=True)
            self._thread.start()
            return

        self._command_target(cmmtype)
        return self._result

    def _command_target(self, cmdtype):
        order = getattr(self, cmdtype+'_order')

        self._result = None
        self._done = list()
        retval = None
        for handler_name in order:
            if self._abort:
                self._abort = False
                break
            handler = self._dev_refs[handler_name]
            func = getattr(handler, 'cmd_turn_'+cmdtype)
            retval = func()
            if retval[0]:
                self._done.append(handler_name)
            else:
                break

        self._result = retval

        self._is_running = ''


class InjSysPUModeHandler(_Devices, _Callback):
    """Device to control pulsed magnets configuration for injection."""

    _DEF_TIMEOUT = 10 # [s]
    _DEF_SLEEP = 0.1  # [s]
    SI_DPKCKR_DEFKICK = -6.7  # [mrad]
    TS_POSANG_DEFDELTA = 2.5  # [mrad]
    SI_DPKCKR_DLYR_ONAXINC = 28  # [count]
    SI_DPKCKR_DLYR_OPT = 0  # [count]

    def __init__(self, print_log=True, callback=None):
        """Init."""
        self.pudpk = PowerSupplyPU(PowerSupplyPU.DEVICES.SI_INJ_DPKCKR)
        self.punlk = PowerSupplyPU(PowerSupplyPU.DEVICES.SI_INJ_NLKCKR)
        self.trigdpk = Trigger('SI-01SA:TI-InjDpKckr')
        self.trignlk = Trigger('SI-01SA:TI-InjNLKckr')
        self.posang = PosAng(PosAng.DEVICES.TS)
        devices = (
            self.pudpk, self.punlk,
            self.trigdpk, self.trignlk,
            self.posang,
        )
        self._print_log = print_log
        self._abort = _Flag()

        # call super init
        _Devices.__init__(self, '', devices)
        _Callback.__init__(self, callback=callback)

    @property
    def is_accum(self):
        """If configuration is Accumulation."""
        if not self.connected:
            return False
        dpk_off = (self.pudpk.pwrstate == PowerSupplyPU.PWRSTATE.Off) or \
            (self.pudpk.pulse == PowerSupplyPU.PULSTATE.Off)
        nlk_on = (self.punlk.pwrstate == PowerSupplyPU.PWRSTATE.On) and \
            (self.punlk.pulse == PowerSupplyPU.PULSTATE.On)
        return dpk_off & nlk_on

    def cmd_switch_to_accum(self):
        """Switch to Accumulation."""
        self._abort.clear()
        self._update_status('Switching to PU Accumulation config...')
        if not self._check_pu_interlocks():
            return False
        if self._check_abort():
            return False

        # if previously in on-axis, do delta angle x
        if self.is_onaxis:
            if not self._do_delta_posang(-self.TS_POSANG_DEFDELTA):
                return False

        # set pulsed magnet pwrstate and pulse
        proced = (
            (self.pudpk.cmd_turn_off_pulse, 'turn DpK pulse off.'),
            (self.pudpk.cmd_turn_off, 'turn DpK off.'),
            (self.punlk.cmd_turn_on, 'turn NLK on.'),
            (self.punlk.cmd_turn_on_pulse, 'turn NLK pulse on.'),
        )
        if not self._do_procedures(proced):
            return False

        self._update_status('PU mode switched to Accumulation!')
        return True

    @property
    def is_optim(self):
        """If configuration is Optimization."""
        if not self.connected:
            return False
        dpk_evt_ok = self.trigdpk.source == self.trignlk.source
        dpk_dly_ok = self.trigdpk.delay_raw == self.SI_DPKCKR_DLYR_OPT
        dpk_kck_ok = self.pudpk.strength == self.SI_DPKCKR_DEFKICK
        dpk_on = (self.pudpk.pwrstate == PowerSupplyPU.PWRSTATE.On) and \
            (self.pudpk.pulse == PowerSupplyPU.PULSTATE.On)
        nlk_on = (self.punlk.pwrstate == PowerSupplyPU.PWRSTATE.On) and \
            (self.punlk.pulse == PowerSupplyPU.PULSTATE.On)
        return dpk_evt_ok & dpk_dly_ok & dpk_kck_ok & dpk_on & nlk_on

    def cmd_switch_to_optim(self):
        """Switch to Optimization."""
        self._abort.clear()
        self._update_status('Switching to PU Optimization config...')
        if not self._check_pu_interlocks():
            return False
        if self._check_abort():
            return False

        # if previously in on-axis, do delta angle x
        if self.is_onaxis:
            if not self._do_delta_posang(-self.TS_POSANG_DEFDELTA):
                return False

        if self._check_abort():
            return False

        # configure DpK trigger
        if not self._config_dpk_trigger(delayraw=self.SI_DPKCKR_DLYR_OPT):
            return False

        # set DpK Kick
        if not self._config_dpk_kick():
            return False

        # set pulsed magnet pwrstate and pulse
        proced = (
            (self.pudpk.cmd_turn_on, 'turn DpK on.'),
            (self.punlk.cmd_turn_on, 'turn NLK on.'),
            (self.pudpk.cmd_turn_on_pulse, 'turn DpK pulse on.'),
            (self.punlk.cmd_turn_on_pulse, 'turn NLK pulse on.'),
        )
        if not self._do_procedures(proced):
            return False

        self._update_status('PU mode switched to Optimization!')
        return True

    @property
    def is_onaxis(self):
        """If configuration is OnAxis."""
        if not self.connected:
            return False
        dpk_evt_ok = self.trigdpk.source == self.trignlk.source
        dpk_dly_ok = self.trigdpk.delay_raw == \
            self.trignlk.delay_raw + self.SI_DPKCKR_DLYR_ONAXINC
        dpk_kck_ok = self.pudpk.strength == self.SI_DPKCKR_DEFKICK
        dpk_on = (self.pudpk.pwrstate == PowerSupplyPU.PWRSTATE.On) and \
            (self.pudpk.pulse == PowerSupplyPU.PULSTATE.On)
        nlk_off = (self.punlk.pwrstate == PowerSupplyPU.PWRSTATE.Off) or \
            (self.punlk.pulse == PowerSupplyPU.PULSTATE.Off)
        return dpk_evt_ok & dpk_dly_ok & dpk_kck_ok & dpk_on & nlk_off

    def cmd_switch_to_onaxis(self):
        """Switch to OnAxis."""
        self._abort.clear()
        self._update_status('Switching to PU OnAxis config...')
        if not self._check_pu_interlocks():
            return False
        if self._check_abort():
            return False

        # if not previously in on-axis, do delta angle x
        if not self.is_onaxis:
            if not self._do_delta_posang(self.TS_POSANG_DEFDELTA):
                return False

        if self._check_abort():
            return False

        # configure DpK trigger
        delay = self.trignlk.delay_raw + self.SI_DPKCKR_DLYR_ONAXINC
        if not self._config_dpk_trigger(delayraw=delay):
            return False

        # set DpK Kick
        if not self._config_dpk_kick():
            return False

        # set pulsed magnet pwrstate and pulse
        proced = (
            (self.punlk.cmd_turn_off_pulse, 'turn NLK pulse off.'),
            (self.punlk.cmd_turn_off, 'turn NLK off.'),
            (self.pudpk.cmd_turn_on, 'turn DpK on.'),
            (self.pudpk.cmd_turn_on_pulse, 'turn DpK pulse on.'),
        )
        if not self._do_procedures(proced):
            return False

        self._update_status('PU mode switched to OnAxis!')
        return True

    def _check_pu_interlocks(self):
        if not self.pudpk.interlock_ok:
            self._update_status('ERR: DpK interlocks not ok. Aborted.')
            return False
        if not self.punlk.interlock_ok:
            self._update_status('ERR: NLK interlocks not ok. Aborted.')
            return False
        return True

    def _do_delta_posang(self, delta):
        if self.posang.need_ref_update:
            self.posang.cmd_update_reference()
        _time.sleep(InjSysPUModeHandler._DEF_SLEEP)
        self.posang.delta_angx += delta
        if not self._wait(self.posang, 'delta_angx', delta):
            self._update_status('ERR:Could not do delta AngX.')
            return False
        return True

    def _config_dpk_trigger(self, delayraw):
        # set DpK trigger event to NLK trigger event
        dpk_event = self.trignlk.source
        self.trigdpk.source = dpk_event
        if not self._wait(self.trigdpk, 'source', dpk_event):
            self._update_status('ERR:Could not set DpK trigger event.')
            return False
        # set DpK trigger DelayRaw
        self.trigdpk.delay_raw = delayraw
        if not self._wait(self.trigdpk, 'delay_raw', delayraw):
            self._update_status('ERR:Could not set DpK trigger delay.')
            return False
        return True

    def _config_dpk_kick(self):
        self.pudpk.strength = self.SI_DPKCKR_DEFKICK
        if not self._wait(self.pudpk, 'strength', self.SI_DPKCKR_DEFKICK):
            self._update_status(
                'ERR:Could not set DpK Kick to '
                f'{self.SI_DPKCKR_DEFKICK:.1f}mrad.')
            return False
        return True

    def _do_procedures(self, procedures):
        for fun, msg in procedures:
            if self._check_abort():
                return False
            if not fun(timeout=2):
                self._update_status('ERR:Could not ' + msg)
                return False
            _time.sleep(0.5)
        return True

    # -------- thread help methods --------

    def cmd_abort(self):
        """Abort PU mode change."""
        self._abort.set()
        self._update_status('WARN:Abort received for PU Mode change.')
        return True

    def _check_abort(self):
        """Clear abort flag."""
        if not self._abort.is_set():
            return False
        self._abort.clear()
        self._update_status('ERR:Aborted PU Mode change.')
        return True

    # ---------- check sp -----------

    def _wait(self, device, prop, desired, tolerance=1e-3, timeout=_DEF_TIMEOUT):
        _t0 = _time.time()
        while _time.time() - _t0 < timeout:
            if abs(getattr(device, prop) - desired) < tolerance:
                return True
            _time.sleep(InjSysPUModeHandler._DEF_SLEEP)
        return False

    # ---------- logging -----------

    def _update_status(self, status):
        if self._print_log:
            print(status)
        self.run_callbacks(status)
