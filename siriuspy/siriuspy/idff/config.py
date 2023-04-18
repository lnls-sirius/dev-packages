"""Insertion Device Feedforward Configuration."""

import numpy as _np

from ..search import IDSearch as _IDSearch
from ..clientconfigdb import ConfigDBDocument as _ConfigDBDocument


class IDFFConfig(_ConfigDBDocument):
    """Insertion Device Feedforward Configuration."""

    CONFIGDB_TYPE = 'si_idff'

    def __init__(self, name=None, url=None):
        """."""
        name = name or 'idff_' + self.generate_config_name()
        super().__init__(
            config_type=IDFFConfig.CONFIGDB_TYPE, name=name, url=url)

    @property
    def name(self):
        """Return configuration name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set configuration name."""
        if self.configdbclient.check_valid_configname(value):
            self._name = value
            self.load()

    @property
    def pparameter_pvname(self):
        """Return ID pparameter pvname."""
        config = self._value
        if config:
            kparm = config['pvnames']['pparameter']
            return kparm
        else:
            raise ValueError('Configuration not loaded!')

    @property
    def kparameter_pvname(self):
        """Return ID kparameter pvname."""
        config = self._value
        if config:
            kparm = config['pvnames']['kparameter']
            return kparm
        else:
            raise ValueError('Configuration not loaded!')

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
            return list(self._value['polarizations'].keys())
        else:
            raise ValueError('Configuration not loaded!')

    def calculate_setpoints(self, polarization, kparameter_value):
        """Return correctors setpoints for a particular ID config.

        The parameter 'kparameter' can be a gap or phase value,
        depending on the insertion device.
        """
        if self._value:
            setpoints = dict()
            idff = self._value['polarizations'][polarization]
            kparameter_values = idff['kparameter']
            setpoints = dict()
            for corrlabel, table in idff.items():
                if corrlabel not in ('pparameter', 'kparameter'):
                    # linear interpolation
                    setpoint = _np.interp(
                        kparameter_value, kparameter_values, table)
                    corr_pvname = self._value['pvnames'][corrlabel]
                    setpoints[corr_pvname] = setpoint
            return setpoints
        else:
            raise ValueError('Configuration not loaded!')

    @staticmethod
    def create_template_config(idname):
        """Create a template configuration for a given ID type."""
        idff = _IDSearch.conv_idname_2_idff(idname)

        # description
        description = 'Config created with IDFFConfig.create_template_config'

        # build value for pvnames key
        pvnames = dict()
        for key, corr_pvname in idff.items():
            if key != 'polarizations':
                pvnames[key] = corr_pvname

        # build value for polarizations key
        ctable = dict()
        for pvname in pvnames:
            ctable[pvname] = [0, 0]
        ptable = dict(ctable)
        ptable['pparameter'] = [0, 0]
        ptable['kparameter'] = 0
        ktable = dict(ctable)
        ktable['pparameter'] = 0
        ktable['kparameter'] = [0, 0]

        polarizations = dict()
        for polarization in idff['polarizations']:
            if polarization == 'none':
                polarizations[polarization] = dict(ptable)
            else:
                polarizations[polarization] = dict(ktable)

        template_config = dict(
            description=description, pvnames=pvnames,
            polarizations=polarizations)
        return template_config

    def _get_corr_pvnames(self, cname1, cname2):
        """Return corrector power supply pvnames."""
        if self._value:
            pvnames = self._value['pvnames']
            corr1, corr2 = pvnames.get(cname1), pvnames.get(cname2)
            return corr1, corr2
        else:
            raise ValueError('Configuration not loaded!')
