"""E-Gun devices."""

import time as _time

from ..pwrsupply.psctrl.pscstatus import PSCStatus as _PSCStatus

from .device import Device as _Device


class EGBias(_Device):
    """EGun Bias Device."""

    DEF_TIMEOUT = 10  # [s]
    PWRSTATE = _PSCStatus.PWRSTATE

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-BiasPS'
        ALL = (LI, )

    _properties = (
        'voltoutsoft', 'voltinsoft', 'currentinsoft', 'switch', 'swstatus')

    def __init__(self, devname=None):
        """."""
        if devname is None:
            devname = EGBias.DEVICES.LI

        # check if device exists
        if devname not in EGBias.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EGBias._properties)

    @property
    def voltage(self):
        """."""
        return self['voltinsoft']

    @voltage.setter
    def voltage(self, value):
        self['voltoutsoft'] = value

    @property
    def current(self):
        """."""
        return self['currentinsoft']

    def cmd_turn_on(self, timeout=DEF_TIMEOUT):
        """."""
        self['switch'] = self.PWRSTATE.On
        return self._wait('swstatus', self.PWRSTATE.On, timeout)

    def cmd_turn_off(self, timeout=DEF_TIMEOUT):
        """."""
        self['switch'] = self.PWRSTATE.Off
        return self._wait('swstatus', self.PWRSTATE.Off, timeout)

    def is_on(self):
        """."""
        return self['swstatus'] == self.PWRSTATE.On

    def set_voltage(self, value, tol=0.2, timeout=DEF_TIMEOUT):
        """Set voltage and wait readback reach value with a tolerance."""
        self.voltage = value
        nrp = int(timeout / 0.1)
        for _ in range(nrp):
            if abs(self.voltage - value) < tol:
                return True
            _time.sleep(0.1)
        print('timed out waiting for EGBias voltage to reach ',
              value, 'with tolerance ', tol)
        return False


class EGFilament(_Device):
    """EGun Filament Device."""

    DEF_TIMEOUT = 10  # [s]
    PWRSTATE = _PSCStatus.PWRSTATE

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-FilaPS'
        ALL = (LI, )

    _properties = (
        'voltinsoft', 'currentinsoft', 'currentoutsoft', 'switch', 'swstatus')

    def __init__(self, devname=None):
        """."""
        if devname is None:
            devname = EGFilament.DEVICES.LI

        # check if device exists
        if devname not in EGFilament.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EGFilament._properties)

    @property
    def voltage(self):
        """."""
        return self['voltinsoft']

    @property
    def current(self):
        """."""
        return self['currentinsoft']

    @current.setter
    def current(self, value):
        """."""
        self['currentoutsoft'] = value

    def cmd_turn_on(self, timeout=DEF_TIMEOUT):
        """."""
        self['switch'] = self.PWRSTATE.On
        return self._wait('swstatus', self.PWRSTATE.On, timeout)

    def cmd_turn_off(self, timeout=DEF_TIMEOUT):
        """."""
        self['switch'] = self.PWRSTATE.Off
        return self._wait('swstatus', self.PWRSTATE.Off, timeout)

    def is_on(self):
        """."""
        return self['swstatus'] == self.PWRSTATE.On


class EGHVPS(_Device):
    """Egun High-Voltage Power Supply Device."""

    DEF_TIMEOUT = 10  # [s]
    PWRSTATE = _PSCStatus.PWRSTATE

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-HVPS'
        ALL = (LI, )

    _properties = (
        'currentinsoft', 'currentoutsoft',
        'voltinsoft', 'voltoutsoft',
        'enable', 'enstatus',
        'switch', 'swstatus')

    def __init__(self, devname=None):
        """."""
        if devname is None:
            devname = EGHVPS.DEVICES.LI

        # check if device exists
        if devname not in EGHVPS.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EGHVPS._properties)

    @property
    def current(self):
        """."""
        return self['currentinsoft']

    @current.setter
    def current(self, value):
        """."""
        self['currentoutsoft'] = value

    @property
    def voltage(self):
        """."""
        return self['voltinsoft']

    @voltage.setter
    def voltage(self, value):
        self['voltoutsoft'] = value

    def cmd_turn_on(self, timeout=DEF_TIMEOUT):
        """."""
        self['enable'] = self.PWRSTATE.On
        if not self._wait('enstatus', self.PWRSTATE.On, timeout=timeout/2):
            return False
        self['switch'] = self.PWRSTATE.On
        return self._wait('swstatus', self.PWRSTATE.On, timeout=timeout/2)

    def cmd_turn_off(self, timeout=DEF_TIMEOUT):
        """."""
        self['enable'] = self.PWRSTATE.Off
        if not self._wait('enstatus', self.PWRSTATE.Off, timeout=timeout/2):
            return False
        self['switch'] = self.PWRSTATE.Off
        return self._wait('swstatus', self.PWRSTATE.Off, timeout=timeout/2)

    def is_on(self):
        """."""
        ison = self['enstatus'] == self.PWRSTATE.On
        ison &= self['swstatus'] == self.PWRSTATE.On
        return ison


class EGTriggerPS(_Device):
    """Egun Trigger Power Supply Device."""

    DEF_TIMEOUT = 10  # [s]

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-TriggerPS'
        ALL = (LI, )

    _properties = (
        'status', 'allow', 'enable', 'enablereal')

    def __init__(self, devname=DEVICES.LI):
        """."""
        # check if device exists
        if devname not in EGTriggerPS.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EGTriggerPS._properties)

    @property
    def status(self):
        """."""
        return self['status']

    @property
    def allow(self):
        """."""
        return self['allow']

    @property
    def enable(self):
        """."""
        return self['enablereal']

    @enable.setter
    def enable(self, value):
        self['enable'] = bool(value)

    def cmd_enable_trigger(self, timeout=DEF_TIMEOUT):
        """."""
        self['enable'] = 1
        return self._wait('enablereal', value=1, timeout=timeout)

    def cmd_disable_trigger(self, timeout=DEF_TIMEOUT):
        """."""
        self['enable'] = 0
        return self._wait('enablereal', value=0, timeout=timeout)

    def is_on(self):
        """."""
        return self['enablereal'] == 1


class EGPulsePS(_Device):
    """Egun Pulse Power Supply Device."""

    DEF_TIMEOUT = 10  # [s]

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-PulsePS'
        ALL = (LI, )

    _properties = (
        'singleselect', 'singleselstatus', 'singleswitch', 'singleswstatus',
        'multiselect', 'multiselstatus', 'multiswitch', 'multiswstatus',
        'poweroutsoft', 'powerinsoft')

    def __init__(self, devname=DEVICES.LI):
        """Init."""
        # check if device exists
        if devname not in EGPulsePS.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EGPulsePS._properties)

    @property
    def single_bunch_mode(self):
        """Single bunch mode."""
        return self['singleselstatus']

    @single_bunch_mode.setter
    def single_bunch_mode(self, value):
        self['singleselect'] = value

    @property
    def single_bunch_switch(self):
        """Single bunch switch."""
        return self['singleswstatus']

    @single_bunch_switch.setter
    def single_bunch_switch(self, value):
        self['singleswitch'] = value

    @property
    def multi_bunch_mode(self):
        """Multi bunch mode."""
        return self['multiselstatus']

    @multi_bunch_mode.setter
    def multi_bunch_mode(self, value):
        self['multiselect'] = value

    @property
    def multi_bunch_switch(self):
        """Multi bunch switch."""
        return self['multiswstatus']

    @multi_bunch_switch.setter
    def multi_bunch_switch(self, value):
        self['multiswitch'] = value

    @property
    def power(self):
        """Power."""
        return self['powerinsoft']

    @power.setter
    def power(self, value):
        self['poweroutsoft'] = value

    def cmd_turn_off_single_bunch_switch(self, timeout=DEF_TIMEOUT):
        """Turn off single bunch switch."""
        self.single_bunch_switch = 0
        return self._wait('singleswstatus', 0, timeout=timeout)

    def cmd_turn_off_single_bunch_mode(self, timeout=DEF_TIMEOUT):
        """Turn off single bunch mode."""
        self.single_bunch_mode = 0
        return self._wait('singleselstatus', 0, timeout=timeout)

    def cmd_turn_off_single_bunch(self, timeout=DEF_TIMEOUT):
        """Turn off single bunch."""
        if not self.cmd_turn_off_single_bunch_switch():
            return False
        return self.cmd_turn_off_single_bunch_mode()

    def cmd_turn_on_single_bunch_switch(self, timeout=DEF_TIMEOUT):
        """Turn on single bunch switch."""
        self.single_bunch_switch = 1
        return self._wait('singleswstatus', 1, timeout=timeout)

    def cmd_turn_on_single_bunch_mode(self, timeout=DEF_TIMEOUT):
        """Turn on single bunch mode."""
        self.single_bunch_mode = 1
        return self._wait('singleselstatus', 1, timeout=timeout)

    def cmd_turn_on_single_bunch(self, timeout=DEF_TIMEOUT):
        """Turn on single bunch."""
        if not self.cmd_turn_on_single_bunch_mode():
            return False
        return self.cmd_turn_on_single_bunch_switch()

    def cmd_turn_off_multi_bunch_switch(self, timeout=DEF_TIMEOUT):
        """Turn off multi bunch switch."""
        self.multi_bunch_switch = 0
        return self._wait('multiswstatus', 0, timeout=timeout)

    def cmd_turn_off_multi_bunch_mode(self, timeout=DEF_TIMEOUT):
        """Turn off multi bunch mode."""
        self.multi_bunch_mode = 0
        return self._wait('multiselstatus', 0, timeout=timeout)

    def cmd_turn_off_multi_bunch(self, timeout=DEF_TIMEOUT):
        """Turn off multi bunch."""
        if not self.cmd_turn_off_multi_bunch_switch():
            return False
        return self.cmd_turn_off_multi_bunch_mode()

    def cmd_turn_on_multi_bunch_switch(self, timeout=DEF_TIMEOUT):
        """Turn on multi bunch switch."""
        self.multi_bunch_switch = 1
        return self._wait('multiswstatus', 1, timeout=timeout)

    def cmd_turn_on_multi_bunch_mode(self, timeout=DEF_TIMEOUT):
        """Turn on multi bunch mode."""
        self.multi_bunch_mode = 1
        return self._wait('multiselstatus', 1, timeout=timeout)

    def cmd_turn_on_multi_bunch(self, timeout=DEF_TIMEOUT):
        """Turn on multi bunch."""
        if not self.cmd_turn_on_multi_bunch_mode():
            return False
        return self.cmd_turn_on_multi_bunch_switch()
