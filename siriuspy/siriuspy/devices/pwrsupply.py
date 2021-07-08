"""Power Supply Devices."""

from .. import util as _util

from ..namesys import SiriusPVName as _SiriusPVName
from ..search import PSSearch as _PSSearch
from ..pwrsupply.psctrl.pscstatus import PSCStatus as _PSCStatus

from .device import Device as _Device


class _PSDev(_Device):
    """Base Power Supply Device."""

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
        'OpMode-Sel', 'OpMode-Sts',
        'WfmUpdateAuto-Sel', 'WfmUpdateAuto-Sts',
    )
    _properties_pulsed = (
        'Voltage-SP', 'Voltage-RB', 'Voltage-Mon',
        'Pulse-Sel', 'Pulse-Sts')

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in _PSSearch.get_psnames():
            raise NotImplementedError(devname)

        # power supply type and magnetic function
        (self._pstype, self._psmodel, self._magfunc,
         self._strength_propty, self._strength_units,
         self._is_linac, self._is_pulsed, self._is_magps) = \
            _PSDev.get_device_type(devname)

        # set attributes
        (self._strength_sp_propty,
         self._strength_rb_propty,
         self._strength_mon_propty,
         properties) = self._set_attributes_properties()

        # call base class constructor
        super().__init__(devname, properties=properties)

    @property
    def pstype(self):
        """Return type of magnet(s) excited by power supply device."""
        return self._pstype

    @property
    def psmodel(self):
        """Return power supply model of the device."""
        return self._psmodel

    @property
    def magfunc(self):
        """Return function of magnet excited by power supply devices."""
        return self._magfunc

    @property
    def is_linac(self):
        """Return True if device is a Linac magnet power supply."""
        return self._is_linac

    @property
    def is_pulsed(self):
        """Return True if device is a pulsed magnet powet supply."""
        return self._is_pulsed

    @property
    def is_magps(self):
        """Return True if device is a Sirius magnet power supply."""
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

    @staticmethod
    def get_device_type(devname):
        """."""
        pstype = _PSSearch.conv_psname_2_pstype(devname)
        psmodel = _PSSearch.conv_psname_2_psmodel(devname)
        magfunc = _PSSearch.conv_psname_2_magfunc(devname)
        strength_propty = _util.get_strength_label(magfunc)
        strength_units = _util.get_strength_units(magfunc, pstype)
        is_linac = devname.sec.endswith('LI')
        is_pulsed = devname.dis == 'PU'
        is_magps = not is_linac and not is_pulsed
        return (pstype, psmodel, magfunc,
                strength_propty, strength_units,
                is_linac, is_pulsed, is_magps)

    # --- private methods ---

    def _set_attributes_properties(self):

        properties = _PSDev._properties_common
        if self._is_linac:
            properties += _PSDev._properties_linac
        else:
            if self._is_pulsed:
                properties += _PSDev._properties_pulsed
            else:
                properties += _PSDev._properties_magps

        # strength properties
        strength_sp_propty = self._strength_propty + '-SP'
        strength_rb_propty = self._strength_propty + '-RB'
        strength_mon_propty = self._strength_propty + '-Mon'
        properties += (
            strength_sp_propty,
            strength_rb_propty,
            strength_mon_propty,
        )

        ret = (
            strength_sp_propty, strength_rb_propty, strength_mon_propty,
            properties)

        return ret


class PowerSupply(_PSDev):
    """Power Supply Device."""

    OPMODE_SEL = _PSCStatus.OPMODE
    OPMODE_STS = _PSCStatus.STATES

    class DEVICES:
        """Devices names."""

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
    DEF_TIMEOUT = 10

    class DEVICES:
        """Devices names."""

        TB_INJ_SEPT = 'TB-04:PU-InjSept'
        BO_INJ_KCKR = 'BO-01D:PU-InjKckr'
        BO_EJE_KCKR = 'BO-48D:PU-EjeKckr'
        TS_EJE_SEPTF = 'TS-01:PU-EjeSeptF'
        TS_EJE_SEPTG = 'TS-01:PU-EjeSeptG'
        TS_INJ_SPETG_1 = 'TS-04:PU-InjSeptG-1'
        TS_INJ_SPETG_2 = 'TS-04:PU-InjSeptG-2'
        TS_INJ_SPETF = 'TS-04:PU-InjSeptF'
        SI_INJ_DPKCKR = 'SI-01SA:PU-InjDpKckr'
        SI_INJ_NLKCKR = 'SI-01SA:PU-InjNLKckr'
        SI_PING_H = 'SI-01SA:PU-PingH'
        SI_PING_V = 'SI-19C4:PU-PingV'
        ALL = (
            TB_INJ_SEPT,
            BO_INJ_KCKR, BO_EJE_KCKR,
            TS_EJE_SEPTF, TS_EJE_SEPTG,
            TS_INJ_SPETG_1, TS_INJ_SPETG_2,
            TS_INJ_SPETF,
            SI_INJ_DPKCKR, SI_INJ_NLKCKR,
            SI_PING_H, SI_PING_V,
        )

    _properties_timing = ('Delay-SP', 'Delay-RB')

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in PowerSupplyPU.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname)

        # create timing device
        self._dev_timing = self._create_timing_device()

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
        return self._dev_timing['Delay-RB']

    @delay.setter
    def delay(self, value):
        """."""
        self._dev_timing['Delay-SP'] = value

    @property
    def pulse(self):
        """."""
        return self['Pulse-Sts']

    @pulse.setter
    def pulse(self, value):
        """."""
        self['Pulse-Sel'] = value

    def cmd_turn_on_pulse(self, timeout=DEF_TIMEOUT):
        """."""
        self.pulse = self.PULSTATE.On
        self._wait('Pulse-Sts', value=self.PULSTATE.On, timeout=timeout)

    def cmd_turn_off_pulse(self, timeout=DEF_TIMEOUT):
        """."""
        self.pulse = self.PULSTATE.Off
        self._wait('Pulse-Sts', value=self.PULSTATE.Off, timeout=timeout)

    @property
    def properties(self):
        """Return device properties."""
        return self._properties + self._dev_timing.properties

    @property
    def pvnames(self):
        """Return device PV names."""
        return set(list(super().pvnames) +
                   list(self._dev_timing.pvnames))

    @property
    def connected(self):
        """Return PVs connection status."""
        if not super().connected:
            return False
        return self._dev_timing.connected

    @property
    def disconnected_pvnames(self):
        """Return list of disconnected device PVs."""
        return set(list(super().disconnected_pvnames) +
                   list(self._dev_timing.disconnected_pvnames))

    def update(self):
        """Update device properties."""
        super().update()
        self._dev_timing.update()

    def pv_object(self, propty):
        """Return PV object for a given device property."""
        if propty in self._pvs:
            return super().pv_object(propty)
        return self._dev_timing.pv_object(propty)

    def pv_attribute_values(self, attribute):
        """Return property-value dict of a given attribute for all PVs."""
        attributes = super().pv_attribute_values(attribute)
        attributes_ti = self._dev_timing.pv_attribute_values(attribute)
        attributes.update(attributes_ti)
        return attributes

    def __getitem__(self, propty):
        """Return value of property."""
        if propty in self._pvs:
            return super().__getitem__(propty)
        return self._dev_timing[propty]

    def __setitem__(self, propty, value):
        """Set value of property."""
        if propty in self._pvs:
            super().__setitem__(propty, value)
        else:
            self._dev_timing[propty] = value

    # --- private methods ---

    def _create_timing_device(self):
        """."""
        devname = self._devname.substitute(dis='TI')
        device = _Device(devname, PowerSupplyPU._properties_timing)
        return device
