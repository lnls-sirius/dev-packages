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
        self._idname = None
        self._polarization_definitions = None
        super().__init__(
            config_type=IDFFConfig.CONFIGDB_TYPE, name=name_, url=url)

    @property
    def idname(self):
        """Return idname corresponding to IDFFConfig."""
        return self._idname

    @idname.setter
    def idname(self, value):
        """Set idname."""
        if value not in _IDSearch.get_idnames():
            raise ValueError(f'{value} is not a valid idname!')
        self._idname = value

    @property
    def pparameter_pvname(self):
        """Return ID pparameter pvname."""
        config = self._value
        if config:
            kparm = config['pvnames']['pparameter']
            return kparm
        else:
            raise ValueError('Configuration not defined!')

    @property
    def kparameter_pvname(self):
        """Return ID kparameter pvname."""
        config = self._value
        if config:
            kparm = config['pvnames']['kparameter']
            return kparm
        else:
            raise ValueError('Configuration not defined!')

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
            raise ValueError('Configuration not defined!')

    @property
    def value(self):
        """Get configuration."""
        return _dcopy(self._value)

    @value.setter
    def value(self, value):
        """Set configuration."""
        self._set_value(value)

    def calculate_setpoints(
            self, polarization, pparameter_value, kparameter_value):
        """Return correctors setpoints for a particular ID config.

        'pparameter' is the ID phase which defines polarization.
        'kparameter' can be a gap or phase value, depending on the ID.
        """
        if self._value:
            setpoints = dict()
            idff = self._value['polarizations'][polarization]
            if polarization == 'none':
                params = idff['pparameter']
                param_value = pparameter_value
            else:
                params = idff['kparameter']
                param_value = kparameter_value
            setpoints = dict()
            for corrlabel, table in idff.items():
                if corrlabel not in ('pparameter', 'kparameter'):
                    # linear interpolation
                    setpoint = _np.interp(param_value, params, table)
                    corr_pvname = self._value['pvnames'][corrlabel]
                    setpoints[corr_pvname] = setpoint
            return setpoints
        else:
            raise ValueError('Configuration not defined!')

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
        ktable['kparameter'] = [0, 0]

        pol2pparam = _IDSearch.conv_idname_2_polarization_pparameter
        polarizations = dict()
        for pol in idff['polarizations']:
            if pol == _IDSearch.POL_UNDEF_STR:
                continue
            if pol == _IDSearch.POL_NONE_STR:
                polarizations[pol] = dict(ptable)
            else:
                ktable['pparameter'] = pol2pparam(idname, pol)
                polarizations[pol] = dict(ktable)

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
        stg += f'\ndescription: {value["description"]}'

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
        self._find_idname()
        self._calc_polariz_defs()

    def get_polarization_state(self, pparameter, kparameter):
        """Return polarization state based on ID parameteres."""
        idname = self._idname
        pol_idx = _IDSearch.conv_idname_2_polarization_state(
            idname, pparameter, kparameter)
        pol_str = _IDSearch.conv_idname_2_polarizations_sts(idname)[pol_idx]
        return pol_str

    def check_valid_value(self, value):
        """Check consistency of SI_IDFF configuration."""
        configs = value['polarizations']
        pvnames = {
            key: value for key, value in value['pvnames'].items()
            if key not in ('pparameter', 'kparameter')}
        corrlabels = set(pvnames.keys())

        # check pvnames in configs
        pvsconfig = set(pvnames.values())
        getch = _IDSearch.conv_idname_2_idff_chnames
        getcv = _IDSearch.conv_idname_2_idff_cvnames
        getqs = _IDSearch.conv_idname_2_idff_qsnames
        chnames = [corr + ':Current-SP' for corr in getch(self.idname)]
        cvnames = [corr + ':Current-SP' for corr in getcv(self.idname)]
        qsnames = [corr + ':Current-SP' for corr in getqs(self.idname)]
        pvsidsearch = set(chnames + cvnames + qsnames)
        symm_diff = pvsconfig ^ pvsidsearch

        if symm_diff:
            raise ValueError('List of pvnames in config is not consistent')

        # check polarizations in configs
        pconfig = set(configs.keys()) - set((_IDSearch.POL_NONE_STR, ))
        pidsearch = set(_IDSearch.conv_idname_2_polarizations(self.idname))
        symm_diff = pconfig ^ pidsearch

        if symm_diff:
            raise ValueError(
                'List of polarizations in config is not consistent')

        # check polarization tables consistency
        for polarization, table in configs.items():
            corrtable = {
                key: value for key, value in table.items()
                if key not in ('pparameter', 'kparameter')}

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
            nrpts_corrtables = {len(table) for table in corrtable.values()}
            nrpts_kparameter = set([len(table[param]), ])
            symm_diff = nrpts_corrtables ^ nrpts_kparameter

            if symm_diff:
                raise ValueError(
                    'Corrector tables and kparameter list in config '
                    'are not consistent')
        return True

    def _get_corr_pvnames(self, cname1, cname2):
        """Return corrector power supply pvnames."""
        if self._value:
            pvnames = self._value['pvnames']
            corr1, corr2 = pvnames.get(cname1), pvnames.get(cname2)
            return corr1, corr2
        else:
            raise ValueError('Configuration not defined!')

    def _set_value(self, value):
        super()._set_value(value)
        self._find_idname()
        self._calc_polariz_defs()

    def _calc_polariz_defs(self):
        """."""
        # fill polarization data struct
        data = self._value['polarizations']
        poldefs = dict()
        for pol, tab in data.items():
            if pol != _IDSearch.POL_NONE_STR:
                poldefs[pol] = tab['pparameter']
            else:
                poldefs[pol] = tab['kparameter']
        self._polarization_definitions = poldefs

    def _find_idname(self):
        """."""
        # find associated idname
        self._idname = None
        pvnames = self._value['pvnames']
        kparameter, pparameter = pvnames['kparameter'], pvnames['pparameter']
        for idname in _IDSearch.get_idnames():
            kparam_propty = _IDSearch.conv_idname_2_kparameter_propty(idname)
            pparam_propty = _IDSearch.conv_idname_2_pparameter_propty(idname)
            if None in (kparam_propty, pparam_propty):
                continue
            kparam = idname + ':' + kparam_propty
            pparam = idname + ':' + pparam_propty

            if kparam == kparameter and pparam == pparameter:
                self._idname = idname
                break
        if self._idname is None:
            # could not find idname
            raise ValueError(
                'kparameter and pparameter in config are not '
                'associated with an idname!')
