"""Insertion Devices Feedforward Devices."""

from ..namesys import SiriusPVName as _SiriusPVName
from ..search import IDSearch as _IDSearch
from ..idff.config import IDFFConfig as _IDFFConfig

from .device import Device as _Device, Devices as _Devices
from .pwrsupply import PowerSupply as _PowerSupply
from .ids import WIG as _WIG, APU as _APU, EPU as _EPU


class IDFF(_Devices):
    """Insertion Device Feedforward Device."""

    class DEVICES:
        """."""
        EPU50_10SB = 'SI-10SB:ID-EPU50'
        WIG180_14SB = 'SI-14SB:ID-WIG180'
        ALL = (
            EPU50_10SB, WIG180_14SB,
            )

    def __init__(self, devname):
        """."""
        devname = _SiriusPVName(devname)

        # check if device exists
        if devname not in IDFF.DEVICES.ALL:
            raise NotImplementedError(devname)

        self._devname = devname  # needed for _create_devices
        self._idffconfig = _IDFFConfig()

        self._kparametername = \
            _IDSearch.conv_idname_2_kparameter_propty(devname)

        self._devkp, self._devsch, self._devscv, self._devsqs = \
            self._create_devices(devname)

        # call base class constructor
        devices = [self._devkp, ]
        devices += self._devsch
        devices += self._devscv
        devices += self._devsqs
        super().__init__(devname=devname, devices=devices)

    @property
    def chnames(self):
        """Return CH corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_chnames(self.devname)

    @property
    def cvnames(self):
        """Return CV corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_cvnames(self.devname)

    @property
    def qsnames(self):
        """Return QS corrector power supply names."""
        return _IDSearch.conv_idname_2_idff_qsnames(self.devname)

    @property
    def kparametername(self):
        """Return corresponding to ID kparameter."""
        return self._kparametername

    @property
    def polarizations(self):
        """Return list of possible light polarizations for the ID."""
        return _IDSearch.conv_idname_2_polarizations(self.devname)

    @property
    def kparameter(self):
        """Return kparameter value."""
        return self._devkp[self._kparametername]

    @property
    def idffconfig(self):
        """."""
        return self._idffconfig

    def load_config(self, name):
        """Load IDFF configuration."""
        self._idffconfig.load_config(name=name)
        if not self._config_is_ok():
            raise ValueError('Config is incompatible with ID configdb type.')

    @property
    def kparameter_pvname(self):
        """Return pvname corresponding to ID kparameter pvname."""
        return self._idffconfig.kparameter_pvname

    def calculate_setpoints(self, polarization):
        """Return correctors setpoints for a particular ID config.

        polarization - a string defining the required polarization for
        setpoint calculation.
        """
        if not self._idffconfig:
            ValueError('IDFFConfig is not loaded!')

        if polarization not in self.idffconfig.polarizations:
            raise ValueError('Polarization is not compatible with ID.')
        kparameter = self.kparameter
        setpoints = self.idffconfig.calculate_setpoints(
            polarization, kparameter)
        return polarization, setpoints

    def implement_setpoints(self, polarization, setpoints=None):
        """Implement setpoints in correctors."""
        if not setpoints:
            _, setpoints = self.calculate_setpoints(polarization)
        corrs = self._devsch + self._devscv
        for pvname, value in setpoints.items():
            for dev in corrs:
                if dev.devname in pvname:
                    pvname = _SiriusPVName(pvname)
                    dev[pvname.propty] = value
                    break

    def _create_devices(self, devname):
        kparm_auto_mon = False
        devkp = _Device(
            devname=devname,
            properties=(self._kparametername, ), auto_mon=kparm_auto_mon)
        devsch = [_PowerSupply(devname=dev) for dev in self.chnames]
        devscv = [_PowerSupply(devname=dev) for dev in self.cvnames]
        devsqs = [_PowerSupply(devname=dev) for dev in self.qsnames]

        return devkp, devsch, devscv, devsqs

    def _config_is_ok(self):
        # TODO: to be implemented
        return True


class WIGIDFF(IDFF):
    """Wiggler Feedforward."""

    class DEVICES(_WIG.DEVICES):
        """."""

    @property
    def gap_mon(self):
        """."""
        return self.kparameter


class EPUIDFF(IDFF):
    """EPU Feedforward."""

    class DEVICES(_EPU.DEVICES):
        """."""

    @property
    def gap_mon(self):
        """."""
        return self.kparameter


class APUIDFF(_Devices):
    """APU Feedforward."""

    class DEVICES(_APU.DEVICES):
        """."""

    @property
    def phase_mon(self):
        """."""
        return self.kparameter
