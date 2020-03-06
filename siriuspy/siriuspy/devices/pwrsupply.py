"""."""

from .. import util as _util
from ..search import PSSearch as _PSSearch
from ..pwrsupply.status import PSCStatus as _PSCStatus

from .device import Device as _Device


class _PSDev(_Device):
    """Power Supply Device."""

    PWRSTATE = _PSCStatus.PWRSTATE

    _default_timeout = 0.5  # [s]
    _properties_common = (
        'PwrState-Sel', 'PwrState-Sts',
    )
    _properties_linac = (
        'Current-SP', 'Current-RB', 'Current-Mon',
    )
    _properties_magps = (
        'Current-SP', 'Current-RB', 'Current-Mon',
        'OpMode-Sel', 'OpMode-Sts'
    )
    _properties_pulsed = (
        'Voltage-SP', 'Voltage-RB',
        'Delay-SP', 'Delay-RB',
        'Pulse-Sel', 'Pulse-Sts')

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in _PSSearch.get_psnames():
            raise NotImplementedError(devname)
        self._devname = devname

        # power supply type and magnetic function
        (self._pstype, self._magfunc,
         self._strength_propty, self._strength_units,
         self._is_linac, self._is_pulsed) = self._get_device_type()

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
    def is_pulsed(self):
        """."""
        return self._is_pulsed

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
        return self[self._strength_rb_propty]

    @strength.setter
    def strength(self, value):
        """."""
        self[self._strength_sp_propty] = value

    @property
    def strength_mon(self):
        """."""
        return self[self._strength_mon_propty]

    @property
    def pwrstate(self):
        """."""
        return self['PwrState-Sts']

    @pwrstate.setter
    def pwrstate(self, value):
        """."""
        self['PwrState-Sel'] = value

    def cmd_turn_on(self, timeout=_default_timeout):
        """."""
        self.pwrstate = self.PWRSTATE.On
        self._wait('PwrState-Sts', self.PWRSTATE.On, timeout=timeout)

    def cmd_turn_off(self, timeout=_default_timeout):
        """."""
        self.pwrstate = self.PWRSTATE.Off
        self._wait('PwrState-Sts', self.PWRSTATE.Off, timeout=timeout)

    # --- private methods ---

    def _get_device_type(self):
        """."""
        pstype = _PSSearch.conv_psname_2_pstype(self._devname)
        magfunc = _PSSearch.conv_psname_2_magfunc(self._devname)
        strength_propty = _util.get_strength_label(magfunc)
        strength_units = _util.get_strength_units(magfunc, pstype)
        is_linac = self._devname.startswith('LI-')
        is_pulsed = ':PU-' in self._devname
        return (pstype, magfunc, strength_propty, strength_units,
                is_linac, is_pulsed)

    def _set_attributes_properties(self):
        strength_sp_propty = self._strength_propty + '-SP'
        strength_rb_propty = self._strength_propty + '-RB'
        strength_mon_propty = self._strength_propty + '-Mon'

        properties = _PSDev._properties_common
        if self._is_linac:
            properties += _PSDev._properties_linac
        else:
            if self._is_pulsed:
                properties += _PSDev._properties_pulsed
            else:
                properties += _PSDev._properties_magps

        ret = (
            strength_sp_propty, strength_rb_propty, strength_mon_propty,
            properties)

        return ret


class PowerSupply(_PSDev):
    """Power Supply Device."""

    OPMODE_SEL = _PSCStatus.OPMODE
    OPMODE_STS = _PSCStatus.STATES

    @property
    def current(self):
        """."""
        return self['Current-RB']

    @current.setter
    def current(self, value):
        self['Current-SP'] = value

    @property
    def current_mon(self):
        """."""
        return self['Current-Mon']

    @property
    def opmode(self):
        """."""
        return self['OpMode-Sts']

    def cmd_slowref(self, timeout=_PSDev._default_timeout):
        """."""
        self['OpMode-Sel'] = self.OPMODE_SEL.SlowRef
        self._wait('OpMode-Sts', self.OPMODE_STS.SlowRef, timeout=timeout)

    def cmd_slowrefsync(self, timeout=_PSDev._default_timeout):
        """."""
        self['OpMode-Sel'] = self.OPMODE_SEL.SlowRefSync
        self._wait('OpMode-Sts', self.OPMODE_STS.SlowRefSync, timeout=timeout)


class PowerSupplyPU(_PSDev):
    """Pulsed Power Supply Device."""

    PULSTATE = _PSCStatus.PWRSTATE

    @property
    def voltage(self):
        """."""
        return self['Voltage-RB']

    @voltage.setter
    def voltage(self, value):
        self['Voltage-SP'] = value

    @property
    def voltage_mon(self):
        """."""
        return self['Voltage-Mon']

    @property
    def delay(self):
        """."""
        return self['Delay-RB']

    @delay.setter
    def delay(self, value):
        """."""
        self['Delay-SP'] = value

    @property
    def pulse(self):
        """."""
        return self['Pulse-Sts']

    @pulse.setter
    def pulse(self, value):
        """."""
        self['Pulse-Sel'] = value

    def cmd_turn_on_pulse(self):
        """."""
        self.pulse = self.PULSTATE.On

    def cmd_turn_off_pulse(self):
        """."""
        self.pulse = self.PULSTATE.Off
