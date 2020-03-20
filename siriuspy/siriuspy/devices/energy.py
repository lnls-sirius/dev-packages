"""Energy Devices."""

from .device import DeviceApp as _DeviceApp


class Energy(_DeviceApp):
    """Energy devices."""

    class DEVICES:
        """."""

        TB = 'TB'
        BO = 'BO'
        TS = 'TS'
        SI = 'SI'
        ALL = (TB, BO, TS, SI)

    _props = (
        'Energy-SP', 'Energy-RB',
        'EnergyRef-Mon', 'Energy-Mon')

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in Energy.DEVICES.ALL:
            raise NotImplementedError(devname)

        # get dipole names
        self._psnames_dipoles = self._get_dipole_devnames(devname)

        # get properties
        properties, self._prop2prop = self._get_properties()

        # call base class constructor
        super().__init__(properties, devname)


    @property
    def synchronized(self):
        """Return True if dipoles are synchronized."""
        props = self._prop2prop['Energy-SP']
        values = {self[prop] for prop in props}
        if len(values) > 1:
            return False
        props = self._prop2prop['Energy-RB']
        values = {self[prop] for prop in props}
        if len(values) > 1:
            return False
        props = self._prop2prop['EnergyRef-Mon']
        values = {self[prop] for prop in props}
        if len(values) > 1:
            return False
        return True

    @property
    def energy(self):
        """Return Ref-Mon energy."""
        props = self._prop2prop['EnergyRef-Mon']
        values = [self[prop] for prop in props]
        return sum(values) / len(values)

    @energy.setter
    def energy(self, value):
        """Set energy."""
        props = self._prop2prop['Energy-SP']
        for prop in props:
            self[prop] = value

    @property
    def energy_sp(self):
        """Return -SP energy."""
        props = self._prop2prop['Energy-SP']
        values = [self[prop] for prop in props]
        return sum(values) / len(values)

    @property
    def energy_mon(self):
        """Return -Mon energy."""
        props = self._prop2prop['Energy-Mon']
        values = [self[prop] for prop in props]
        return sum(values) / len(values)

    def _get_properties(self):
        properties = list()
        prop2prop = dict()
        for psname in self._psnames_dipoles:
            for propty in Energy._props:
                pvname = psname + ':' + propty
                if propty not in prop2prop:
                    prop2prop[propty] = [pvname]
                else:
                    prop2prop[propty].append(pvname)
                properties.append(pvname)
        return properties, prop2prop

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
