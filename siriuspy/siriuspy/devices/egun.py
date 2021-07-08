"""."""

from ..pwrsupply.psctrl.pscstatus import PSCStatus as _PSCStatus

from .device import Device as _Device


class EGBias(_Device):
    """EGun Bias Device."""

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
        """."""
        self['voltoutsoft'] = value

    @property
    def current(self):
        """."""
        return self['currentinsoft']

    def cmd_turn_on(self):
        """."""
        self['switch'] = self.PWRSTATE.On

    def cmd_turn_off(self):
        """."""
        self['switch'] = self.PWRSTATE.Off

    def is_on(self):
        """."""
        return self['swstatus'] == self.PWRSTATE.On


class EGFilament(_Device):
    """EGun Filament Device."""

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

    def cmd_turn_on(self):
        """."""
        self['switch'] = self.PWRSTATE.On

    def cmd_turn_off(self):
        """."""
        self['switch'] = self.PWRSTATE.Off

    def is_on(self):
        """."""
        return self['swstatus'] == self.PWRSTATE.On


class EGHVPS(_Device):
    """Egun High-Voltage Power Supply Device."""

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

    def cmd_turn_on(self):
        """."""
        self['enable'] = self.PWRSTATE.On
        self['switch'] = self.PWRSTATE.On

    def cmd_turn_off(self):
        """."""
        self['enable'] = self.PWRSTATE.Off
        self['switch'] = self.PWRSTATE.Off

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
        self._wait('enablereal', value=1, timeout=timeout)

    def cmd_disable_trigger(self, timeout=DEF_TIMEOUT):
        """."""
        self['enable'] = 0
        self._wait('enablereal', value=0, timeout=timeout)

    def is_on(self):
        """."""
        return self['enablereal'] == 1
