"""Energy Devices."""

from .syncd import DevicesSync as _DevicesSync


class Energy(_DevicesSync):
    """Energy devices."""

    class DEVICES:
        """."""

        TB = 'TB'
        BO = 'BO'
        TS = 'TS'
        SI = 'SI'
        ALL = (TB, BO, TS, SI)

    _props_sync = ('Energy-SP', 'Energy-RB', 'EnergyRef-Mon')
    _props_async = ('Energy-Mon', )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in Energy.DEVICES.ALL:
            raise NotImplementedError(devname)

        # get dipole names
        psnames_dip = self._get_dipole_devnames(devname)

        # call base class constructor
        super().__init__(
            psnames_dip,
            Energy._props_sync, Energy._props_async, devname)

    @property
    def energy(self):
        """Return Ref-Mon energy."""
        return self.value_get('EnergyRef-Mon')

    @energy.setter
    def energy(self, value):
        """Set energy."""
        self.value_set('Energy-SP', value)

    @property
    def energy_sp(self):
        """Return -SP energy."""
        return self.value_get('Energy-SP')

    @property
    def energy_mon(self):
        """Return -Mon energy."""
        return self.value_get('Energy-Mon')

    @staticmethod
    def _get_dipole_devnames(devname):
        if devname == Energy.DEVICES.TB:
            psnames_dipoles = ('TB-Fam:PS-B', )
        elif devname == Energy.DEVICES.BO:
            psnames_dipoles = ('BO-Fam:PS-B-1', 'BO-Fam:PS-B-2')
        elif devname == Energy.DEVICES.TS:
            psnames_dipoles = ('TS-Fam:PS-B', )
        elif devname == Energy.DEVICES.SI:
            psnames_dipoles = ('SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2')
        return psnames_dipoles
