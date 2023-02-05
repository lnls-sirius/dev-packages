"""Insertion Device Feedforward Configuration."""

from ..search import IDSearch as _IDSearch
from ..clientconfigdb import ConfigDBDocument as _ConfigDBDocument


class IDFFConfig:
    """."""
    CONFIGDB_TYPE = 'si_idff'

    def __init__(self, name=None):
        """."""    
        self._name = None
        self._configdbdoc = None
        self._value = None
        if name:
            self.load_config(name=self._name)

    @property
    def name(self):
        """Configuration name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set configuration name."""
        self._name = value

    @property
    def kparameter_pvname(self):
        """Return IR kparameter pvname."""
        config = self._value
        if config:
            pvnames = config['kparameter']
            kparm = pvnames.get('kparameter')
        else:
            raise ValueError('Configuration not loaded!')
        return kparm

    @property
    def ch_pvnames(self):
        """Return CH corrector power supply pvnames."""
        return self._get_corr_pvnames('ch1', 'ch2')

    @property
    def cv_pvnames(self):
        """Return CV corrector power supply pvnames."""
        return self._get_corr_pvnames('cv1', 'cv2')

    @property
    def qs_pvnames(self):
        """Return QS corrector power supply pvnames."""
        return self._get_corr_pvnames('qs1', 'qs2')

    @property
    def polarizations(self):
        """Return list of light polarizations in the IDFF config."""
        if self._value:
            return list(self._values['polarizations'].keys())
        else:
            raise ValueError('Configuration not loaded!')

    @property
    def value(self):
        """Return ID feedforward table."""
        return self._value

    @value.setter
    def value(self, value):
        """Set ID feedforward table."""
        # TODO: check dictionary
        self._value = value

    def interpolate_setpoints(self, polarization, kparameter):
        """Return correctors setpoints for a particular ID config.

        The parameter 'kparameter' can be a gap or phase value,
        depending on the insertion device.
        """
        # NOTE: not implemented yet
        setpoints = dict()
        return setpoints

    @staticmethod
    def create_config(idname):
        """Create a template configuration for a given ID type."""
        idff = _IDSearch.conv_idname_2_idff(idname)
        
        # build value for pvnames key
        pvnames = dict()
        for key, corr_pvname in idff.items():
            if key != 'polarizations':
                pvnames[key] = corr_pvname
        
        # build value for polarizations key
        table = dict(kparameter=[0, ])
        for pvname in pvnames:
            table[pvname] = [0, ]
        polarizations = dict()
        for polarization in idff['polarizations']:
            polarizations[polarization] = dict(table)
        
        template_config = dict(pvnames=pvnames, polarizations=polarizations)
        return template_config

    def load_config(self, name=None):
        """Load IDFF configuration."""
        if name is not None:
            self._name = name
        self._configdbdoc = _ConfigDBDocument(
            config_type=IDFFConfig.CONFIGDB_TYPE, name=self._name)
        self._configdbdoc.load()
        self._value = self._configdbdoc.value

    def save_config(self, name=None):
        """Save IDFF configuration."""
        if name is not None:
            self._name = name
        self._configdbdoc = _ConfigDBDocument(
            config_type=IDFFConfig.CONFIGDB_TYPE, name=self._name)
        self._configdbdoc.value = self._value
        self._configdbdoc.save()

    def _get_corr_pvnames(self, cname1, cname2):
        """Return corrector power supply pvnames."""
        if self._value:
            pvnames = self._value['pvnames']
            corr1, corr2 = pvnames.get(cname1), pvnames.get(cname2)
            return corr1, corr2
        else:
            raise ValueError('Configuration not loaded!')
        

    

