#!/usr/bin/env python-sirius
"""."""

from .. import util as _util
from ..search import PSSearch as _PSSearch
from ..pwrsupply.status import PSCStatus as _PSCStatus

from .device import Device as _Device


class PowerSupply(_Device):
    """Power Supply Device."""

    PWRSTATE = _PSCStatus.PWRSTATE
    OPMODE_SEL = _PSCStatus.OPMODE
    OPMODE_STS = _PSCStatus.STATES

    _default_timeout = 0.5  # [s]
    _properties = (
        'Current-SP', 'Current-RB', 'Current-Mon',
        'PwrState-Sel', 'PwrState-Sts')

    def __init__(self, devname):
        """."""
        self._devname = devname

        # power supply type and magnetic function
        (self._pstype, self._magfunc,
         self._strength_propty, self._strength_units,
         self._is_linac) = self._get_device_type()

        # set attributes
        (self._strength_sp_propty,
         self._strength_rb_propty,
         self._strength_mon_propty,
         properties) = self._set_attributes_properties()

        # call base class constructor
        super().__init__(devname, properties=properties)

    @property
    def pstype(self):
        """."""
        return self._pstype

    @property
    def magfunc(self):
        """."""
        return self._magfunc

    @property
    def is_linac(self):
        """."""
        return self._is_linac

    @property
    def current(self):
        """."""
        return self.get('Current-RB')

    @current.setter
    def current(self, value):
        self._pvs['Current-SP'].value = value

    @property
    def current_mon(self):
        """."""
        return self.get('Current-Mon')

    @property
    def strength_property(self):
        """."""
        return self._strength_propty

    @property
    def strength_units(self):
        """."""
        return self._strength_units

    @property
    def strength(self):
        """."""
        return self.get(self._strength_rb_propty)

    @strength.setter
    def strength(self, value):
        """."""
        self._pvs[self._strength_sp_propty].value = value

    @property
    def strength_mon(self):
        """."""
        return self.get(self._strength_mon_propty)

    @property
    def pwrstate(self):
        """."""
        return self.get('PwrState-Sts')

    @pwrstate.setter
    def pwrstate(self, value):
        """."""
        self._pvs['PwrState-Sel'].value = value

    @property
    def opmode(self):
        """."""
        return self.get('OpMode-Sts')

    def cmd_turn_on(self, timeout=_default_timeout):
        """."""
        self.pwrstate = self.PWRSTATE.On
        self._wait('PwrState-Sts', self.PWRSTATE.On, timeout=timeout)

    def cmd_turn_off(self, timeout=_default_timeout):
        """."""
        self.pwrstate = self.PWRSTATE.Off
        self._wait('PwrState-Sts', self.PWRSTATE.Off, timeout=timeout)

    def cmd_slowref(self, timeout=_default_timeout):
        """."""
        self._pvs['OpMode-Sel'].value = self.OPMODE_SEL.SlowRef
        self._wait('OpMode-Sts', self.OPMODE_STS.SlowRef, timeout=timeout)

    def cmd_slowrefsync(self, timeout=_default_timeout):
        """."""
        self._pvs['OpMode-Sel'].value = self.OPMODE_SEL.SlowRefSync
        self._wait('OpMode-Sts', self.OPMODE_STS.SlowRefSync, timeout=timeout)

    # --- private methods ---

    def _get_device_type(self):
        """."""
        pstype = _PSSearch.conv_psname_2_pstype(self._devname)
        magfunc = _PSSearch.conv_psname_2_magfunc(self._devname)
        strength_propty = _util.get_strength_label(magfunc)
        strength_units = _util.get_strength_units(magfunc, pstype)
        is_linac = self._devname.startswith('LI-')
        return pstype, magfunc, strength_propty, strength_units, is_linac

    def _set_attributes_properties(self):
        strength_sp_propty = self._strength_propty + '-SP'
        strength_rb_propty = self._strength_propty + '-RB'
        strength_mon_propty = self._strength_propty + '-Mon'

        props_opmode = tuple() if self._is_linac else \
            ('OpMode-Sel', 'OpMode-Sts')

        properties = \
            PowerSupply._properties + \
            props_opmode + \
            (strength_sp_propty, strength_rb_propty, strength_mon_propty)

        ret = (
            strength_sp_propty, strength_rb_propty, strength_mon_propty,
            properties)

        return ret
