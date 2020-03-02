#!/usr/bin/env python-sirius
"""."""

from ..pwrsupply.status import PSCStatus as _PSCStatus

from .device import Device as _Device


class EGBias(_Device):
    """."""

    PWRSTATE = _PSCStatus.PWRSTATE

    _properties = (
        'voltoutsoft', 'voltinsoft', 'currentinsoft', 'switch', 'swstatus')

    def __init__(self):
        """."""
        # call base class constructor
        super().__init__('LI-01:EG-BiasPS', properties=EGBias._properties)

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
    """."""

    PWRSTATE = _PSCStatus.PWRSTATE

    _properties = (
        'voltinsoft', 'currentinsoft', 'currentoutsoft', 'switch', 'swstatus')

    def __init__(self):
        """."""
        # call base class constructor
        super().__init__('LI-01:EG-FilaPS', properties=EGFilament._properties)

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
    """."""

    PWRSTATE = _PSCStatus.PWRSTATE

    _properties = (
        'currentinsoft', 'currentoutsoft',
        'voltinsoft', 'voltoutsoft',
        'enable', 'enstatus',
        'switch', 'swstatus')

    def __init__(self):
        """."""
        # call base class constructor
        super().__init__('LI-01:EG-HVPS', properties=EGHVPS._properties)

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
