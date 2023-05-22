"""Insertion Device Feedforward Configuration."""

from copy import deepcopy as _dcopy

import numpy as _np

from ..search import IDSearch as _IDSearch
from ..clientconfigdb import ConfigDBDocument as _ConfigDBDocument


class IDFFConfig(_ConfigDBDocument):
    """Insertion Device Feedforward Configuration."""

    CONFIGDB_TYPE = 'si_idff'

    def __init__(self, name=None, url=None):
        """."""
        name_ = name or 'idff_' + self.generate_config_name()
        self._polarization_definitions = None
        super().__init__(
            config_type=IDFFConfig.CONFIGDB_TYPE, name=name_, url=url)

    @property
    def name(self):
        """Return configuration name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set configuration name."""
        if self.configdbclient.check_valid_configname(value):
            self._name = value

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

    @property
    def value(self):
        """Get configuration."""
        return _dcopy(self._value)

    @value.setter
    def value(self, value):
        """Set configuration."""
        self._set_value(value)

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

    def __str__(self):
        """."""
        stg = ''
        stg += f'name: {self.name}'
        value = self.value
        if value is None:
            return stg

        stg += '\n--- pvnames ---'
        pvnames = ''.join(
            [f'\n{key}: {value}' for key, value in value['pvnames'].items()])
        stg += pvnames

        for pol, table in self.value['polarizations'].items():
            stg += f'\n--- {pol} ---'
            for key, value in table.items():
                if isinstance(value, (int, float)):
                    nrpts = 1
                    str_ = f'{value}'
                else:
                    nrpts = len(value)
                    str_ = f'{min(value)}..{max(value)} [{nrpts}]'
                stg += f'\n{key} : ' + str_
        return stg

    def load(self, discarded=False):
        """."""
        super().load(discarded=discarded)
        self._calc_polariz_defs()

    def get_polarization_state(self, pparameter, kparameter):
        """Return polarization state based on ID parameteres."""
        PPARAM_TOL = 0.1
        KPARAM_TOL = 0.1
        poldefs = self._polarization_definitions
        if poldefs is None:
            raise ValueError('No IDFF configuration defined.')
        for pol, val in poldefs.items():
            if pol == 'none':
                continue
            if abs(pparameter - val) < PPARAM_TOL:
                return pol
        if abs(kparameter - poldefs['none']) < KPARAM_TOL:
            return 'none'
        return 'not_defined'

    def check_valid_value(self, value):
        """."""
        if not super().check_valid_value(value):
            return False
        for pol, table in value['polarizations'].items():
            if pol == 'none':
                nrpts = len(table['pparameter'])
            else:
                nrpts = len(table['kparameter'])
            for key, value_ in table.items():
                if key in ('kparameter', 'pparameter'):
                    continue
                if len(value_) != nrpts:
                    return False
        return True

    def _get_corr_pvnames(self, cname1, cname2):
        """Return corrector power supply pvnames."""
        if self._value:
            pvnames = self._value['pvnames']
            corr1, corr2 = pvnames.get(cname1), pvnames.get(cname2)
            return corr1, corr2
        else:
            raise ValueError('Configuration not loaded!')

    def _set_value(self, value):
        super()._set_value(value)
        self._calc_polariz_defs()

    def _calc_polariz_defs(self):
        """."""
        data = self._value['polarizations']
        poldefs = dict()
        for pol, tab in data.items():
            if pol != 'none':
                poldefs[pol] = tab['pparameter']
            else:
                poldefs[pol] = tab['kparameter']
        self._polarization_definitions = poldefs
