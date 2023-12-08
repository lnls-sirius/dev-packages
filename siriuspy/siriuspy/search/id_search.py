"""ID Search module."""

import copy as _copy

from mathphys.functions import get_namedtuple as _get_namedtuple

from ..namesys import SiriusPVName as _SiriusPVName
from ..namesys import Filter as _Filter


class IDSearch:
    """ID Search Class."""

    # NOTE: Maybe we should move these mappings to
    # static tables in our cs-constants server.

    # NOTE: see
    # https://wiki-sirius.lnls.br/mediawiki/index.php/Machine:Insertion_Devices

    _beamline2idname = {
        'CARNAUBA': 'SI-06SB:ID-APU22',  # titular: VPU19
        'CATERETE': 'SI-07SP:ID-APU22',  # titular: VPU19
        'EMA':      'SI-08SB:ID-APU22',  # titular: IVU18
        'MANACA':   'SI-09SA:ID-APU22',  # titular: 2 x APU22
        'SABIA':    'SI-10SB:ID-DELTA52',  # titular: 2 x DELTA52 (EPU50 prev.)
        'IPE':      'SI-11SP:ID-APU58',  # titular: 2 x APPLE-II
        'PAINEIRA': 'SI-14SB:ID-WIG180',  # titular: IVU18
        'SAPUCAIA': 'SI-17SA:ID-PAPU50',  # titular: 2 x APU22
    }

    _idname2beamline = {v: k for k, v in _beamline2idname.items()}

    _idparam_fields = (
        'PERIOD_LENGTH',  # [mm]
        'KPARAM_MIN',  # [mm]
        'KPARAM_MAX',  # [mm]
        'KPARAM_PARKED',  # [mm]
        'KPARAM_POL_CHANGE',  # [mm]
        'KPARAM_TOL',  # [mm]
        'PPARAM_MIN',  # [mm]
        'PPARAM_MAX',  # [mm]
        'PPARAM_PARKED',  # [mm]
        'PPARAM_TOL',  # [mm]
        )

    _idname2params = {
        'SI-06SB:ID-APU22': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                22,
                0, 11, 11, 0, 0.01,
                None, None, None, None)),
        'SI-07SP:ID-APU22': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                22,
                0, 11, 11, 0, 0.01,
                None, None, None, None)),
        'SI-08SB:ID-APU22': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                22,
                0, 11, 11, 0, 0.01,
                None, None, None, None)),
        'SI-09SA:ID-APU22': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                22,
                0, 11, 11, 0, 0.01,
                None, None, None, None)),
        # NOTE: for EPU50 there is a large discrepancy
        # between RB/SP/Mon phase values
        'SI-10SB:ID-EPU50': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                50,
                +22, +300, +300, +300, 0.1,
                -25, 25, 0, 0.5)),
        'SI-10SB:ID-DELTA52': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                52.5,
                -52.5/2, +52.5/2, 0, 0, 0.020,
                -52.5/2, +52.5/2, 0, 0.010)),
        'SI-11SP:ID-APU58': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                58,
                0, 29, 29, 0, 0.01,
                None, None, None, None)),
        'SI-14SB:ID-WIG180': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                180,
                49.73, 49.73, 150, 150, 0.1,
                None, None, None, None)),
        'SI-17SA:ID-PAPU50': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                50,
                0, 25, 25, 0, 0.1,
                None, None, None, None)),
    }

    POL_NONE_STR = 'none'
    POL_UNDEF_STR = 'undef'

    _idname2pol_sel = {
        'SI-06SB:ID-APU22': {
            0: ('horizontal', None),  # [mm]
        },
        'SI-07SP:ID-APU22': {
            0: ('horizontal', None),  # [mm]
        },
        'SI-08SB:ID-APU22': {
            0: ('horizontal', None),  # [mm]
        },
        'SI-09SA:ID-APU22': {
            0: ('horizontal', None),  # [mm]
        },
        'SI-10SB:ID-EPU50': {
            0: ('circularn', -16.36),  # [mm]
            1: ('horizontal', 0.00),  # [mm]
            2: ('circularp', +16.36),  # [mm]
            3: ('vertical', 25.00),  # [mm]
        },
        'SI-10SB:ID-DELTA52': {
            0: ('circularn', -52.5/4),  # [mm]
            1: ('horizontal', 0.00),  # [mm]
            2: ('circularp', +52.5/4),  # [mm]
            3: ('vertical', -52.5/2),  # [mm]
        },
        'SI-11SP:ID-APU58': {
            0: ('horizontal', None),  # [mm]
        },
        'SI-17SA:ID-PAPU50': {
            0: ('horizontal', None),  # [mm]
        },
    }
    _idname2pol_sts = _copy.deepcopy(_idname2pol_sel)
    _idname2pol_sts['SI-10SB:ID-EPU50'].update(
        {4: (POL_NONE_STR, None), 5: (POL_UNDEF_STR, None)})
    _idname2pol_sts['SI-10SB:ID-DELTA52'].update(
        {4: (POL_NONE_STR, None), 5: (POL_UNDEF_STR, None)})

    _idname_2_idff = {
        'SI-06SB:ID-APU22': None,
        'SI-07SP:ID-APU22': None,
        'SI-08SB:ID-APU22': None,
        'SI-09SA:ID-APU22': None,
        'SI-10SB:ID-EPU50': {
            'polarizations': tuple(
                item[0] for item in
                _idname2pol_sts['SI-10SB:ID-EPU50'].values()),
            'pparameter': 'SI-10SB:ID-EPU50:Phase-Mon',
            'kparameter': 'SI-10SB:ID-EPU50:Gap-Mon',
            'ch1': 'SI-10SB:PS-CH-1:Current-SP',  # upstream
            'ch2': 'SI-10SB:PS-CH-2:Current-SP',  # downstream
            'cv1': 'SI-10SB:PS-CV-1:Current-SP',
            'cv2': 'SI-10SB:PS-CV-2:Current-SP',
            'qs1': 'SI-10SB:PS-QS-1:Current-SP',
            'qs2': 'SI-10SB:PS-QS-2:Current-SP',
        },
        'SI-10SB:ID-DELTA52': {
            'polarizations': tuple(
                item[0] for item in
                _idname2pol_sts['SI-10SB:ID-DELTA52'].values()),
            'pparameter': 'SI-10SB:ID-DELTA52:PParam-Mon',
            'kparameter': 'SI-10SB:ID-DELTA52:KParam-Mon',
            'ch1': 'SI-10SB:PS-CH-1:Current-SP',  # upstream
            'ch2': 'SI-10SB:PS-CH-2:Current-SP',  # downstream
            'cv1': 'SI-10SB:PS-CV-1:Current-SP',
            'cv2': 'SI-10SB:PS-CV-2:Current-SP',
            'qs1': 'SI-10SB:PS-QS-1:Current-SP',
            'qs2': 'SI-10SB:PS-QS-2:Current-SP',
        },
        'SI-11SP:ID-APU58': None,
        'SI-14SB:ID-WIG180': {
            'polarizations': ('horizontal', ),
            'pparameter': None,
            'kparameter': 'SI-14SB:ID-WIG180:Gap-Mon',
            'ch1': 'SI-14SB:PS-CH-1:Current-SP',  # upstream
            'ch2': 'SI-14SB:PS-CH-2:Current-SP',  # downstream
        },
        'SI-17SA:ID-PAPU50': {
            'polarizations': ('horizontal', ),
            'pparameter': None,
            'kparameter': 'SI-17SA:ID-PAPU50:Phase-Mon',
            'ch1': 'SI-17SA:PS-CH-1:Current-SP',  # upstream
            'ch2': 'SI-17SA:PS-CH-2:Current-SP',  # downstream
            'cv1': 'SI-17SA:PS-CV-1:Current-SP',
            'cv2': 'SI-17SA:PS-CV-2:Current-SP',
        },
    }

    @staticmethod
    def get_idnames(filters=None):
        """Return a sorted and filtered list of all ID names."""
        idnames_list = list(IDSearch._idname_2_idff.keys())
        idnames = _Filter.process_filters(idnames_list, filters=filters)
        return sorted(idnames)

    @staticmethod
    def get_beamlines(filters=None):
        """Return a sorted and filtered list of all ID beamlines."""
        beamlines_list = list(IDSearch._idname2beamline.values())
        beamlines = _Filter.process_filters(beamlines_list, filters=filters)
        return sorted(beamlines)

    @staticmethod
    def conv_idname_2_beamline(idname):
        """Return the beam line name corresponding to sector."""
        if idname in IDSearch._idname2beamline.keys():
            return IDSearch._idname2beamline[idname]
        return None

    @staticmethod
    def conv_beamline_2_idname(beamline):
        """Return the beam line name corresponding to idname."""
        if beamline in IDSearch._beamline2idname.keys():
            return IDSearch._beamline2idname[beamline]
        return None

    @staticmethod
    def get_idname_2_beamline_dict():
        """Return idname to beamline dictionary."""
        return IDSearch._idname2beamline.copy()

    @staticmethod
    def get_beamline_2_idname_dict():
        """Return beamline to idname dictionary."""
        return IDSearch._beamline2idname.copy()

    @staticmethod
    def conv_idname_2_parameters(idname):
        """Return ID parameters from idname."""
        return IDSearch._idname2params[idname]

    @staticmethod
    def conv_idname_2_idff(idname):
        """Return the IDFF dictionary for a given ID name."""
        idff = IDSearch._idname_2_idff[idname]
        if idff is None:
            return None
        return _copy.deepcopy(idff)

    @staticmethod
    def conv_idname_2_pparameter_propty(idname):
        """."""
        idff = IDSearch.conv_idname_2_idff(idname)
        if idff is None:
            return None
        pparameter = idff['pparameter']
        if pparameter:
            pvname = _SiriusPVName(pparameter)
            return pvname.propty
        else:
            return None

    @staticmethod
    def conv_idname_2_kparameter_propty(idname):
        """."""
        idff = IDSearch.conv_idname_2_idff(idname)
        if idff is None:
            return None
        kparameter = idff['kparameter']
        if kparameter:
            pvname = _SiriusPVName(kparameter)
            return pvname.propty
        else:
            return None

    @staticmethod
    def conv_idname_2_idff_chnames(idname):
        """."""
        return IDSearch._get_devname_from_idff(idname, ('ch1', 'ch2'))

    @staticmethod
    def conv_idname_2_idff_cvnames(idname):
        """."""
        return IDSearch._get_devname_from_idff(idname, ('cv1', 'cv2'))

    @staticmethod
    def conv_idname_2_idff_qsnames(idname):
        """."""
        return IDSearch._get_devname_from_idff(idname, ('qs1', 'qs2'))

    @staticmethod
    def conv_idname_2_polarizations(idname):
        """Return ID polarizations (sel)."""
        pols = IDSearch._idname2pol_sel[idname]
        return tuple(pol[0] for pol in pols.values())

    @staticmethod
    def conv_idname_2_polarizations_sts(idname):
        """Return ID polarizations (sts)."""
        pols = IDSearch._idname2pol_sts[idname]
        return tuple(pol[0] for pol in pols.values())

    @staticmethod
    def conv_idname_2_polarization_state(idname, pparameter, kparameter):
        """Return polarization state index."""
        params = IDSearch.conv_idname_2_parameters(idname)
        pols_sts = IDSearch._idname2pol_sts[idname]

        # check if polarization is defined
        for pol_idx, pol in pols_sts.items():
            _, pol_phase = pol
            if pol_phase is None:  # ignore none and undef configs
                continue
            if abs(pparameter - pol_phase) <= params.PPARAM_TOL:
                return pol_idx

        pol_state_sts = IDSearch.conv_idname_2_polarizations_sts(idname)

        # checking if changing polarization
        if abs(kparameter - params.KPARAM_POL_CHANGE) <= params.KPARAM_TOL:
            pol_idx = pol_state_sts.index(IDSearch.POL_NONE_STR)
            return pol_idx

        # at this point the configuration must be undefined
        pol_idx = pol_state_sts.index(IDSearch.POL_UNDEF_STR)
        return pol_idx

    @staticmethod
    def conv_idname_2_polarization_pparameter(idname, pol):
        """Return pparameter value of a given polarization."""
        pols = IDSearch._idname2pol_sel[idname]
        if isinstance(pol, int):
            return pols[pol][1]
        elif isinstance(pol, str):
            for pol_name, pol_pparam in pols.values():
                if pol == pol_name:
                    return pol_pparam
            raise ValueError(f'Invalid polarization string "{pol}"')
        else:
            raise TypeError('Invalid polarization type.')

    # --- private ----

    @staticmethod
    def _get_devname_from_idff(idname, correctors):
        idff = IDSearch.conv_idname_2_idff(idname)
        corrs = list()
        for corr in correctors:
            if corr in idff:
                pvname = _SiriusPVName(idff[corr])
                corrs.append(pvname.device_name)
        return corrs
