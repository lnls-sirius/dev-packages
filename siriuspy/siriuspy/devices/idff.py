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

        self._pparametername = \
            _IDSearch.conv_idname_2_pparameter_propty(devname)

        self._kparametername = \
            _IDSearch.conv_idname_2_kparameter_propty(devname)

        self._devpp, self._devkp, self._devsch, self._devscv, self._devsqs = \
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
    def chdevs(self):
        """Return CH corrector power supply devices."""
        return self._devsch

    @property
    def cvdevs(self):
        """Return CV corrector power supply devices."""
        return self._devscv

    @property
    def qsdevs(self):
        """Return QS corrector power supply names."""
        return self._devsqs

    @property
    def pparametername(self):
        """Return corresponding to ID pparameter."""
        return self._pparametername

    @property
    def kparametername(self):
        """Return corresponding to ID kparameter."""
        return self._kparametername

    @property
    def polarizations(self):
        """Return list of possible light polarizations for the ID."""
        return _IDSearch.conv_idname_2_polarizations(self.devname)

    @property
    def pparameter_mon(self):
        """Return pparameter value."""
        return self._devpp[self._pparametername]

    @property
    def kparameter_mon(self):
        """Return kparameter value."""
        return self._devkp[self._kparametername]

    @property
    def idffconfig(self):
        """."""
        return self._idffconfig

    def find_configs(self):
        """Find si_idff configurations in configdb."""
        return self._idffconfig.configdbclient.find_configs()

    def load_config(self, name):
        """Load IDFF configuration."""
        self._idffconfig.name = name
        if self._idffconfig.name == name:
            self._idffconfig.load()
        else:
            raise ValueError('Could not load configuration.')

    def calculate_setpoints(
            self, pparameter_value=None, kparameter_value=None):
        """Return correctors setpoints for a particular ID config.

        polarization - a string defining the required polarization for
        setpoint calculation.
        """
        polarization, pparameter_value, kparameter_value = \
            self.get_polarization_state(
                pparameter_value=pparameter_value,
                kparameter_value=kparameter_value)

        if not self._idffconfig:
            ValueError('IDFFConfig is not loaded!')

        if polarization not in self.idffconfig.polarizations:
            raise ValueError('Polarization is not compatible with ID.')
        if kparameter_value is None:
            kparameter_value = self.kparameter_mon
        setpoints = self.idffconfig.calculate_setpoints(
            polarization, kparameter_value)
        return setpoints, polarization, pparameter_value, kparameter_value

    def implement_setpoints(
            self, setpoints=None, corrdevs=None):
        """Implement setpoints in correctors."""
        if setpoints is None:
            setpoints, polarization, pparameter_value, kparameter_value = \
                self.calculate_setpoints(
                    pparameter_value=None,
                    kparameter_value=None)
        if corrdevs is None:
            corrdevs = self._devsch + self._devscv + self._devsqs
        for pvname, value in setpoints.items():
            # find corrdev corresponding to pvname
            for dev in corrdevs:
                if dev.devname in pvname:
                    pvname = _SiriusPVName(pvname)
                    dev[pvname.propty] = value
                    break
        return polarization, pparameter_value, kparameter_value

    def check_valid_value(self, value):
        """Check consistency of SI_IDFF configuration."""
        if not super().check_valid_value(value):
            raise ValueError('Value incompatible with config template')

        configs = value['polarizations']
        pvnames = {key: value for key, value in value['pvnames'] \
            if key not in ('pparameters', 'kparameters')}
        corrlabels = set(pvnames.keys())

        # check pvnames in configs
        pvsconfig = set(pvnames.values())
        pvsidsearch = set(self.chnames + self.cvnames + self.qsnames)
        symm_diff = pvsconfig ^ pvsidsearch
        if symm_diff:
            raise ValueError('List of pvnames in config is not consistent')

        # check polarizations in configs
        pconfig = set(configs.keys())
        pidsearch = set(_IDSearch.conv_idname_2_polarizations(self.devname))
        symm_diff = pconfig ^ pidsearch
        if symm_diff:
            raise ValueError(
                'List of polarizations in config is not consistent')

        # check polarization tables consistency
        for polarization, table in configs.items():
            corrtable = {key: value for key, value in table \
                if key not in ('pparameters', 'kparameters')}

            # check 'pparameter'
            if 'pparameter' not in table:
                raise ValueError(
                    'Missing pparameter in polarization configuration.')

            # check 'kparameter'
            if 'kparameter' not in table:
                raise ValueError(
                    'Missing kparameter in polarization configuration.')

            # check corr label list
            corrlabels_config = set(corrtable.keys())
            symm_diff = corrlabels ^ corrlabels_config
            if symm_diff:
                raise ValueError(
                    'List of corrlabels in config is not consistent')

            # check nrpts in tables
            param = 'pparameter' if polarization == 'none' else 'kparameter'
            nrpts_corrtables = set([len(table) for table in corrtable.values()])
            nrpts_kparameter = set([len(table[param]), ])
            symm_diff = nrpts_corrtables ^ nrpts_kparameter
            if symm_diff:
                msg = (
                    'Corrector tables and kparameter list in config'
                    ' are not consistent')
                raise ValueError(msg)

        return True

    def get_polarization_state(
            self, pparameter_value=None, kparameter_value=None):
        """."""
        if pparameter_value is None:
            pparameter_value = self.pparameter_mon
        if kparameter_value is None:
            kparameter_value = self.kparameter_mon
        polarization = self.idffconfig.get_polarization_state(
            pparameter=pparameter_value, kparameter=kparameter_value)
        return polarization, pparameter_value, kparameter_value

    def _create_devices(self, devname):
        param_auto_mon = False
        devpp = _Device(
            devname=devname,
            properties=(self._pparametername, ), auto_mon=param_auto_mon)
        devkp = _Device(
            devname=devname,
            properties=(self._kparametername, ), auto_mon=param_auto_mon)
        devsch = [_PowerSupply(devname=dev) for dev in self.chnames]
        devscv = [_PowerSupply(devname=dev) for dev in self.cvnames]
        devsqs = [_PowerSupply(devname=dev) for dev in self.qsnames]

        return devpp, devkp, devsch, devscv, devsqs


class WIGIDFF(IDFF):
    """Wiggler Feedforward."""

    class DEVICES(_WIG.DEVICES):
        """."""

    @property
    def gap_mon(self):
        """."""
        return self.kparameter_mon


class EPUIDFF(IDFF):
    """EPU Feedforward."""

    class DEVICES(_EPU.DEVICES):
        """."""

    @property
    def phase_mon(self):
        """."""
        return self.pparameter_mon

    @property
    def gap_mon(self):
        """."""
        return self.kparameter_mon


class APUIDFF(_Devices):
    """APU Feedforward."""

    class DEVICES(_APU.DEVICES):
        """."""

    @property
    def phase_mon(self):
        """."""
        return self.kparameter_mon
