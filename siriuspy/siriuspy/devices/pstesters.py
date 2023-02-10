"""Devices to be used in power supply procedures."""

import time as _time
import numpy as _np

from ..util import get_bit as _get_bit
from ..search import PSSearch as _PSSearch
from ..pwrsupply.csdev import Const as _PSC, ETypes as _PSE, \
    PS_LI_INTLK_THRS as _PS_LI_INTLK, \
    get_ps_interlocks as _get_ps_interlocks
from .device import Device as _Device, Devices as _Devices


DEFAULT_CAP_BANK_VOLT = {
    'FBP_DCLink': 100,
    'PA-RaPSE01:PS-DCLink-BO': 240,
    'PA-RaPSE02:PS-DCLink-BO': 240,
    'PA-RaPSE03:PS-DCLink-BO': 240,
    'PA-RaPSE04:PS-DCLink-BO': 240,
    'PA-RaPSE06:PS-DCLink-BO': 240,
    'PA-RaPSE07:PS-DCLink-BO': 240,
    'PA-RaPSE08:PS-DCLink-BO': 240,
    'PA-RaPSE09:PS-DCLink-BO': 240,
    'PA-RaPSF01:PS-DCLink-BO': 240,
    'PA-RaPSF02:PS-DCLink-BO': 240,
    'PA-RaPSF03:PS-DCLink-BO': 240,
    'PA-RaPSF04:PS-DCLink-BO': 240,
    'PA-RaPSF06:PS-DCLink-BO': 240,
    'PA-RaPSF07:PS-DCLink-BO': 240,
    'PA-RaPSF08:PS-DCLink-BO': 240,
    'PA-RaPSF09:PS-DCLink-BO': 240,
    'PA-RaPSC01:PS-DCLink-BO': 300,
    'PA-RaPSC02:PS-DCLink-BO': 300,
}


class _TesterBase(_Device):
    """Tester base."""


class _TesterPSBase(_TesterBase):
    """Tester PS base."""

    def reset(self):
        """Reset."""
        self['Reset-Cmd'] = 1

    def set_opmode(self, state):
        """Set OpMode."""
        self['OpMode-Sel'] = state

    def check_opmode(self, state):
        """Check OpMode."""
        if isinstance(state, (list, tuple)):
            return self['OpMode-Sts'] in state
        return self['OpMode-Sts'] == state

    def set_pwrstate(self, state='on'):
        """Set PwrState."""
        if state == 'on':
            state = _PSC.PwrStateSel.On
        else:
            state = _PSC.PwrStateSel.Off
        self['PwrState-Sel'] = state

    def check_pwrstate(self, state='on'):
        """Check PwrState."""
        if state == 'on':
            is_ok = self['PwrState-Sts'] == _PSC.PwrStateSts.On
            is_ok &= self['OpMode-Sts'] == _PSC.States.SlowRef
        else:
            is_ok = self['PwrState-Sts'] == _PSC.PwrStateSts.Off
            is_ok &= self['OpMode-Sts'] == _PSC.States.Off
        return is_ok

    def set_ctrlloop(self):
        """Set CtrlLoop."""
        self['CtrlLoop-Sel'] = _PSC.OpenLoop.Closed

    def check_ctrlloop(self):
        """Check CtrlLoop."""
        return self['CtrlLoop-Sts'] == _PSC.OpenLoop.Closed


class TesterDCLinkFBP(_TesterPSBase):
    """FBP DCLink tester."""

    _properties = (
        'Reset-Cmd', 'IntlkSoft-Mon', 'IntlkHard-Mon',
        'OpMode-Sel', 'OpMode-Sts',
        'PwrState-Sel', 'PwrState-Sts',
        'CtrlLoop-Sel', 'CtrlLoop-Sts',
        'Voltage-SP', 'Voltage-Mon',
    )

    def __init__(self, devname):
        """Init."""
        super().__init__(devname, properties=TesterDCLinkFBP._properties)

    def check_intlk(self):
        """Check interlocks."""
        status = (self['IntlkHard-Mon'] == 0)
        status &= (self['IntlkSoft-Mon'] == 0)
        return status

    def check_init_ok(self):
        """Check OpMode in SlowRef."""
        status = (self['OpMode-Sts'] == _PSC.States.SlowRef)
        return status

    def set_ctrlloop(self):
        """Set CtrlLoop."""
        self['CtrlLoop-Sel'] = _PSC.OpenLoop.Open

    def check_ctrlloop(self):
        """Check CtrlLoop."""
        return self['CtrlLoop-Sts'] == _PSC.OpenLoop.Open

    def set_capvolt(self):
        """Set capacitor bank voltage."""
        key = 'FBP_DCLink' if self.devname not in DEFAULT_CAP_BANK_VOLT \
            else self.devname
        self['Voltage-SP'] = DEFAULT_CAP_BANK_VOLT[key]

    def check_capvolt(self):
        """Do not need to check."""
        return True

    def check_status(self):
        """Check Status."""
        return self.check_intlk()

    def check_comm(self):
        """Check Communication."""
        pvo = self.pv_object('PwrState-Sts')
        return not pvo.status != 0


class TesterDCLink(_TesterPSBase):
    """DCLink tester."""

    _properties = (
        'Reset-Cmd',
        'OpMode-Sel', 'OpMode-Sts',
        'PwrState-Sel', 'PwrState-Sts',
        'CtrlLoop-Sel', 'CtrlLoop-Sts',
        'CapacitorBankVoltage-SP', 'CapacitorBankVoltageRef-Mon',
        'CapacitorBankVoltage-Mon')

    def __init__(self, devname):
        """Init."""
        properties = list(TesterDCLink._properties)
        self._intlk_pvs = _get_ps_interlocks(psname=devname)
        properties.extend(self._intlk_pvs)

        super().__init__(devname, properties)

    def check_intlk(self):
        """Check interlocks."""
        status = True
        for intlk in self._intlk_pvs:
            status &= (self[intlk] == 0)
        return status

    def check_init_ok(self):
        """Check OpMode in SlowRef."""
        return self['OpMode-Sts'] == _PSC.States.SlowRef

    def set_capvolt(self):
        """Set capacitor bank voltage."""
        self['CapacitorBankVoltage-SP'] = DEFAULT_CAP_BANK_VOLT[self.devname]

    def check_capvolt(self):
        """Check capacitor bank voltage."""
        return self._cmp(
            self['CapacitorBankVoltage-Mon'],
            DEFAULT_CAP_BANK_VOLT[self.devname])

    def check_status(self):
        """Check status."""
        status = self.check_intlk()
        if self.check_pwrstate():
            status &= self._cmp(
                self['CapacitorBankVoltage-Mon'],
                self['CapacitorBankVoltageRef-Mon'])
        return status

    def check_comm(self):
        """Check communication."""
        pvo = self.pv_object('PwrState-Sts')
        return not pvo.status != 0

    def _cmp(self, value, target):
        if None in [value, target]:
            return False
        return _np.isclose(value, target, rtol=0.05)


class TesterDCLinkRegatron(_TesterBase):
    """DCLink tester."""

    _OPMODE_STS_OFF = 4  # READY
    _OPMODE_STS_ON = 8  # RUN
    _properties = (
        'Reset-Cmd', 'GenIntlk-Mon', 'GenWarn-Mon', 'OpMode-Sts',
        'PwrState-Sel', 'PwrState-Sts',
        'Voltage-SP', 'VoltageRef-Mon', 'Voltage-Mon')

    def __init__(self, devname):
        """Init."""
        super().__init__(devname, TesterDCLinkRegatron._properties)

    def reset(self):
        """Reset."""
        self['Reset-Cmd'] = 1

    def check_intlk(self):
        """Check interlocks."""
        status = (self['GenIntlk-Mon'] == 0)
        status &= (self['GenWarn-Mon'] == 0)
        return status

    def set_pwrstate(self, state='on'):
        """Set PwrState."""
        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        self['PwrState-Sel'] = state

    def check_pwrstate(self, state='on'):
        """Check PwrState."""
        if state == 'on':
            is_ok = self['PwrState-Sts'] == _PSC.OffOn.On
            is_ok &= self['OpMode-Sts'] == self._OPMODE_STS_ON
        else:
            is_ok = self['PwrState-Sts'] == _PSC.OffOn.Off
            is_ok &= self['OpMode-Sts'] == self._OPMODE_STS_OFF
        return is_ok

    def check_init_ok(self):
        """Check OpMode Ok."""
        return self['OpMode-Sts'] == self._OPMODE_STS_ON

    def check_capvolt(self):
        """Check voltage."""
        return _np.isclose(
            self['Voltage-Mon'], self['VoltageRef-Mon'], rtol=0.05)

    def check_status(self):
        """Check status."""
        status = self.check_intlk()
        if self.check_pwrstate():
            status &= self.check_capvolt()
        return status

    def check_comm(self):
        """Check commucation."""
        pvo_intlk = self.pv_object('GenIntlk-Mon')
        pvo_volt = self.pv_object('Voltage-Mon')
        prob = pvo_intlk.status != 0 or pvo_volt.status != 0
        return not prob


class TesterPS(_TesterPSBase):
    """PS tester."""

    _properties = (
        'Reset-Cmd',
        'OpMode-Sel', 'OpMode-Sts',
        'PwrState-Sel', 'PwrState-Sts',
        'CtrlLoop-Sel', 'CtrlLoop-Sts',
        'Current-SP', 'CurrentRef-Mon', 'Current-Mon')

    def __init__(self, devname):
        """Init."""
        properties = list(TesterPS._properties)
        self._intlk_pvs = _get_ps_interlocks(psname=devname)
        properties.extend(self._intlk_pvs)
        if _PSSearch.conv_psname_2_psmodel(devname) == 'FBP':
            properties.extend(['SOFBMode-Sel', 'SOFBMode-Sts'])

        super().__init__(devname, properties)

        splims = _PSSearch.conv_psname_2_splims(devname)
        self.test_current = splims['TSTV']
        self.test_tol = splims['TSTR']

    def check_intlk(self):
        """Check interlocks."""
        status = True
        for intlk in self._intlk_pvs:
            status &= (self[intlk] == 0)
        return status

    def set_current(self, test=False, value=None):
        """Set current."""
        if value is None:
            if test:
                value = self.test_current
            else:
                value = 0
        self['Current-SP'] = value

    def check_current(self, test=False, value=None):
        """Check current."""
        if value is None:
            if test:
                value = self.test_current
            else:
                value = 0
        return self._cmp(self['Current-Mon'], value)

    def check_status(self):
        """Check Status."""
        status = self.check_intlk()
        if self.check_pwrstate():
            status &= self._cmp(
                self['Current-Mon'], self['CurrentRef-Mon'])
        return status

    def check_comm(self):
        """Check Communication."""
        pvo = self.pv_object('PwrState-Sts')
        return not pvo.status != 0

    def _cmp(self, value, target):
        if None in [value, target]:
            return False
        return abs(value - target) < self.test_tol


class TesterPSFBP(TesterPS):
    """PS FBP Tester."""

    def set_sofbmode(self, state='on'):
        """Set SOFBMode."""
        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        self['SOFBMode-Sel'] = state

    def check_sofbmode(self, state='on'):
        """Check SOFBMode."""
        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        return self['SOFBMode-Sts'] == state


class TesterPSLinac(_TesterBase):
    """Linac PS tester."""

    _properties = (
        'StatusIntlk-Mon', 'IntlkWarn-Mon',
        'PwrState-Sel', 'PwrState-Sts',
        'Current-SP', 'Current-Mon',
        'Connected-Mon')

    def __init__(self, devname):
        super().__init__(devname, properties=TesterPSLinac._properties)

        self.intlkwarn_bit = _PSE.LINAC_INTLCK_WARN.index('LoadI Over Thrs')

        splims = _PSSearch.conv_psname_2_splims(devname)
        self.test_current = splims['TSTV']
        self.test_tol = splims['TSTR']

    def check_intlk(self):
        """Check interlocks."""
        intlkval = self['StatusIntlk-Mon']
        if self.devname.dev == 'Spect':
            intlkwarn = self['IntlkWarn-Mon']
            if _get_bit(intlkwarn, self.intlkwarn_bit):
                intlkval -= 2**self.intlkwarn_bit
        return intlkval < _PS_LI_INTLK

    def set_pwrstate(self, state='on'):
        """Set PwrState."""
        if state == 'on':
            state = _PSC.PwrStateSel.On
        else:
            state = _PSC.PwrStateSel.Off
        self['PwrState-Sel'] = state

    def check_pwrstate(self, state='on'):
        """Check PwrState."""
        if state == 'on':
            state = _PSC.PwrStateSel.On
        else:
            state = _PSC.PwrStateSel.Off
        return self['PwrState-Sts'] == state

    def set_current(self, test=False, value=None):
        """Set current."""
        if value is None:
            if test:
                value = self.test_current
            else:
                value = 0
        self['Current-SP'] = value

    def check_current(self, test=False, value=None):
        """Check current."""
        if value is None:
            value = self.test_current if test else 0
        return self._cmp(self['Current-Mon'], value)

    def check_status(self):
        """Check Status."""
        status = self.check_intlk()
        if self.check_pwrstate():
            status &= self._cmp(
                self['Current-Mon'], self['Current-SP'])
        return status

    def check_comm(self):
        """Check Comminication."""
        pvo = self.pv_object('Connected-Mon')
        prob = pvo.value != 0 or pvo.status != 0
        return not prob

    def _cmp(self, value, target):
        if None in [value, target]:
            return False
        return abs(value - target) < self.test_tol


class TesterPSFOFB(_TesterBase):
    """FOFB PS tester."""

    _properties = (
        'AlarmsAmp-Mon',
        'PwrState-Sel', 'PwrState-Sts',
        'Current-SP', 'CurrentRef-Mon', 'Current-Mon',
        'OpMode-Sel', 'OpMode-Sts',
    )

    def __init__(self, devname):
        """Init."""
        super().__init__(devname, properties=TesterPSFOFB._properties)

        splims = _PSSearch.conv_psname_2_splims(devname)
        self.test_current = splims['TSTV']
        self.test_tol = splims['TSTR']

    def set_opmode(self, state):
        """Set opmode to 'state'."""
        self['OpMode-Sel'] = state

    def check_opmode(self, state):
        """Check whether power supply is in opmode 'state'."""
        if isinstance(state, (list, tuple)):
            return self['OpMode-Sts'] in state
        return self['OpMode-Sts'] == state

    def check_intlk(self):
        """Check interlocks."""
        return self['AlarmsAmp-Mon'] == 0

    def set_pwrstate(self, state='on'):
        """Set PwrState."""
        value = _PSC.OffOn.On if state == 'on' else _PSC.OffOn.Off
        self['PwrState-Sel'] = value

    def check_pwrstate(self, state='on'):
        """Check PwrState."""
        value = _PSC.OffOn.On if state == 'on' else _PSC.OffOn.Off
        return self['PwrState-Sts'] == value

    def set_current(self, test=False, value=None):
        """Set current."""
        if value is None:
            if test:
                value = self.test_current
            else:
                value = 0
        self['Current-SP'] = value

    def check_current(self, test=False, value=None):
        """Check current."""
        if value is None:
            if test:
                value = self.test_current
            else:
                value = 0
        return self._cmp(self['Current-Mon'], value)

    def check_status(self):
        """Check Status."""
        status = self.check_intlk()
        if self.check_pwrstate():
            status &= self._cmp(
                self['Current-Mon'], self['CurrentRef-Mon'])
        return status

    def check_comm(self):
        """Check Communication."""
        return self.pv_object('PwrState-Sts').connected

    def _cmp(self, value, target):
        if None in [value, target]:
            return False
        return abs(value - target) < self.test_tol


class _TesterPUBase(_TesterBase):
    """Tester PU base."""

    _properties = (
        'Reset-Cmd',
        'Intlk1-Mon', 'Intlk2-Mon', 'Intlk3-Mon', 'Intlk4-Mon',
        'Intlk5-Mon', 'Intlk6-Mon', 'Intlk7-Mon',
        'PwrState-Sel', 'PwrState-Sts',
        'Pulse-Sel', 'Pulse-Sts',
        'Voltage-SP', 'Voltage-RB', 'Voltage-Mon')
    _sept_properties = _properties
    _kckr_properties = _properties + ('Intlk8-Mon', )

    def __init__(self, devname):
        """Init."""
        if 'Kckr' in devname:
            properties = _TesterPUBase._kckr_properties
        else:
            properties = _TesterPUBase._sept_properties
        super().__init__(devname, properties=properties)

        splims = _PSSearch.conv_psname_2_splims(devname)
        self.test_voltage = splims['TSTV']
        self.test_tol = splims['TSTR']

    def reset(self):
        """Reset."""
        self['Reset-Cmd'] = 1

    def check_intlk(self):
        """Check interlocks."""
        raise NotImplementedError

    def set_pulse(self, state='on'):
        """Set Pulse."""
        # if pulsed magnet was in interlock state and was reset,
        # we need to send a Pulse-Sel = Off before continue
        if self['Pulse-Sel'] == _PSC.OffOn.On \
                and self.check_pulse('off'):
            self['Pulse-Sel'] = _PSC.OffOn.Off
            _time.sleep(0.5)

        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        self['Pulse-Sel'] = state

    def check_pulse(self, state='on'):
        """Check Pulse."""
        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        return self['Pulse-Sts'] == state

    def set_pwrstate(self, state='on'):
        """Set PwrState."""
        # if pulsed magnet was in interlock state and was reset,
        # we need to send a PwrState-Sel = Off before continue
        if self['PwrState-Sel'] == _PSC.OffOn.On \
                and self.check_pwrstate('off'):
            self['PwrState-Sel'] = _PSC.OffOn.Off
            _time.sleep(0.5)

        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        self['PwrState-Sel'] = state

    def check_pwrstate(self, state='on'):
        """Check PwrState."""
        if state == 'on':
            state = _PSC.OffOn.On
        else:
            state = _PSC.OffOn.Off
        return self['PwrState-Sts'] == state

    def set_voltage(self, test=False):
        """Set voltage."""
        value = self.test_voltage if test else 0
        self['Voltage-SP'] = value

    def check_voltage(self, test=False):
        """Check voltage."""
        value = self.test_voltage if test else 0
        return self._cmp(self['Voltage-Mon'], value)

    def check_status(self):
        """Check status."""
        status = self.check_intlk()
        if self.check_pwrstate():
            status &= self._cmp(
                self['Voltage-Mon'], self['Voltage-RB'])
        return status

    def _cmp(self, value, target):
        if None in [value, target]:
            return False
        return abs(value - target) < self.test_tol


class TesterPUKckr(_TesterPUBase):
    """Kicker tester."""

    def check_intlk(self):
        """Check interlocks."""
        status = (self['Intlk1-Mon'] == 1)
        status &= (self['Intlk2-Mon'] == 1)
        status &= (self['Intlk3-Mon'] == 1)
        status &= (self['Intlk4-Mon'] == 1)
        status &= (self['Intlk5-Mon'] == 1)
        status &= (self['Intlk6-Mon'] == 1)
        status &= (self['Intlk7-Mon'] == 1)
        status &= (self['Intlk8-Mon'] == 1)
        return status


class TesterPUSept(_TesterPUBase):
    """Septum tester."""

    def check_intlk(self):
        """Check interlocks."""
        status = (self['Intlk1-Mon'] == 1)
        status &= (self['Intlk2-Mon'] == 1)
        status &= (self['Intlk3-Mon'] == 1)
        status &= (self['Intlk4-Mon'] == 1)
        status &= (self['Intlk5-Mon'] == 1)
        status &= (self['Intlk6-Mon'] == 1)
        status &= (self['Intlk7-Mon'] == 1)
        return status


class Trigger(_Device):
    """Trigger device."""

    _properties = (
        'State-Sel', 'State-Sts',
    )

    def __init__(self, devname):
        """Init trigger."""
        super().__init__(devname, Trigger._properties)

    @property
    def state(self):
        """State."""
        return self['State-Sts']

    @state.setter
    def state(self, value):
        self['State-Sel'] = value


class Triggers(_Devices):
    """Triggers."""

    def __init__(self, devnames):
        """Init triggers."""
        devices, devrefs = list(), dict()
        for devname in devnames:
            dev = Trigger(devname)
            devrefs[devname] = dev
            devices.append(dev)
        self._devrefs = devrefs
        super().__init__('', devices=devices)

    @property
    def triggers(self):
        """Trigger names."""
        return self._devrefs
