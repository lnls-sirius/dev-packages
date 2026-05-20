"""ID Search module."""

import copy as _copy
from threading import Lock as _Lock

from mathphys.functions import get_namedtuple as _get_namedtuple

from .. import util as _util
from .. import clientweb as _web

from ..magnet.excdata import ExcitationData as _ExcitationData
from ..namesys import Filter as _Filter, SiriusPVName as _SiriusPVName


class IDSearch:
    """ID Search Class."""

    # NOTE: Maybe we should move these mappings to
    # static tables in our cs-constants server.

    # NOTE: see
    # https://wiki-sirius.lnls.br/mediawiki/index.php/Machine:Insertion_Devices

    _beamline2idname = {
        'CARNAUBA': 'SI-06SB:ID-VPU29',  # titular: VPU29
        'CATERETE': 'SI-07SP:ID-VPU29',  # titular: VPU29
        'EMA':      'SI-08SB:ID-IVU18',  # titular: IVU18 (APU22 prev.)
        'MANACA':   'SI-09SA:ID-APU22',  # titular: 2 x APU22
        'SABIA':    'SI-10SB:ID-DELTA52',  # titular: 2 x DELTA52 (EPU50 prev.)
        'IPE':      'SI-11SP:ID-UE44',  # titular: 2 x APPLE-II
        'PAINEIRA': 'SI-14SB:ID-IVU18',  # titular: IVU18 (WIG18 prev.)
        'SAPUCAIA': 'SI-17SA:ID-APU22',  # titular: 2 x APU22 (PAPU50 prev.)
        'ARIRANHA': 'SI-20SB:ID-APU22',
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
        'CPARAM_MIN',  # [mm]
        'CPARAM_MAX',  # [mm]
        'CPARAM_PARKED',  # [mm]
        'CPARAM_TOL',  # [mm]
        'CPARAM_POL_CHANGE',  # [mm]
        )

    _idname2params = {
        'SI-06SB:ID-VPU29': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                29,
                9.7, 80, 80, 80, 0.01,
                None, None, None, None,
                None, None, None, None, None)),
        'SI-07SP:ID-VPU29': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                29,
                9.7, 80, 80, 80, 0.01,
                None, None, None, None,
                None, None, None, None, None)),
        'SI-08SB:ID-APU22': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                22,
                0, 11, 11, 0, 0.01,
                None, None, None, None,
                None, None, None, None, None)),
        'SI-08SB:ID-IVU18': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                18.5,
                4.2, 24, 24, 24, 0.01,
                None, None, None, None,
                None, None, None, None, None)),
        'SI-09SA:ID-APU22': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                22,
                0, 11, 11, 0, 0.01,
                None, None, None, None,
                None, None, None, None, None)),
        # NOTE: for EPU50 there is a large discrepancy
        # between RB/SP/Mon phase values
        'SI-10SB:ID-EPU50': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                50,
                +22, +300, +300, +300, 0.1,
                -25, 25, 0, 0.5,
                None, None, None, None, None)),
        'SI-10SB:ID-DELTA52': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                52.5,
                -52.5/2, +52.5/2, 0, 0, 0.020,
                -52.5/2, +52.5/2, 0, 0.010,
                None, None, None, None, None)),
       'SI-11SP:ID-UE44': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                44,
                1, 21, 21, 21, 0.01,
                -13.3, 22, 0, 0.01,
                0, 10.65, 0, 0.01, 0)),
        'SI-14SB:ID-WIG180': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                180,
                49.73, 49.73, 150, 150, 0.1,
                None, None, None, None,
                None, None, None, None, None)),
        'SI-14SB:ID-IVU18': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                18.5,
                4.2, 24, 24, 24, 0.01,
                None, None, None, None,
                None, None, None, None, None)),
        'SI-17SA:ID-PAPU50': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                50,
                0, 25, 25, 0, 0.1,
                None, None, None, None,
                None, None, None, None, None)),
        'SI-17SA:ID-APU22': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                22,
                0, 11, 11, 0, 0.01,
                None, None, None, None,
                None, None, None, None, None)),
        'SI-20SB:ID-APU22': _get_namedtuple(
            'IDParameters',
            _idparam_fields, (
                22,
                0, 11, 11, 0, 0.01,
                None, None, None, None,
                None, None, None, None, None)),
    }

    POL_NONE_STR = 'none'
    POL_UNDEF_STR = 'undef'

    _idname2pol_sel = {
        'SI-06SB:ID-VPU29': {
            0: ('vertical', None),  # [mm]
        },
        'SI-07SP:ID-VPU29': {
            0: ('vertical', None),  # [mm]
        },
        'SI-08SB:ID-APU22': {
            0: ('horizontal', None),  # [mm]
        },
        'SI-08SB:ID-IVU18': {
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
        'SI-11SP:ID-UE44': {
            0: ('circularp', -13.31),  # [mm]
            1: ('horizontal', 0.00),  # [mm]
            2: ('circularn', 13.31),  # [mm]
            3: ('vertical', 22.00),  # [mm]
        },
        'SI-11SP:ID-SIMUL': {
            0: ('horizontal', None),  # [mm]
        },
        'SI-14SB:ID-IVU18': {
            0: ('horizontal', None),  # [mm]
        },
        'SI-17SA:ID-PAPU50': {
            0: ('horizontal', None),  # [mm]
        },
        'SI-17SA:ID-APU22': {
            0: ('horizontal', None),  # [mm]
        },
        'SI-20SB:ID-APU22': {
            0: ('horizontal', None),  # [mm]
        },
    }
    _idname2pol_sts = _copy.deepcopy(_idname2pol_sel)
    _idname2pol_sts['SI-10SB:ID-EPU50'].update(
        {4: (POL_NONE_STR, None), 5: (POL_UNDEF_STR, None)})
    _idname2pol_sts['SI-10SB:ID-DELTA52'].update(
        {4: (POL_NONE_STR, None), 5: (POL_UNDEF_STR, None)})

    # define IDFF correctors labeling (and ordering)
    # NOTE: the ordering within each category here follows the ordering of the
    # correctors in the rack cabinets.
    IDFF_CH_LABELS = ('ch_1', 'ch_2')
    IDFF_CV_LABELS = ('cv_1', 'cv_2')
    IDFF_QS_LABELS = ('qs_1', 'qs_2')
    IDFF_LC_LABELS = ('lch_1', 'lcv_1', 'lcv_2')
    IDFF_QN_LABELS = ('qd1_1', 'qf_1', 'qd2_1', 'qd2_2', 'qf_2', 'qd1_2')
    IDFF_CC_LABELS = ('cc1_1', 'cc2_1', 'cc1_2', 'cc2_2')

    _idname_2_idff = {
        'SI-06SB:ID-VPU29':  {
            'polarizations': ('vertical', ),
            'pparameter': None,
            'kparameter': 'SI-06SB:ID-VPU29:KParam-Mon',
            IDFF_CC_LABELS[0]: 'SI-06SB:PS-CC1-1:Current-SP',  # upstream
            IDFF_CC_LABELS[1]: 'SI-06SB:PS-CC2-1:Current-SP',  # upstream
            IDFF_CC_LABELS[2]: 'SI-06SB:PS-CC1-2:Current-SP',  # downstream
            IDFF_CC_LABELS[3]: 'SI-06SB:PS-CC2-2:Current-SP',  # downstream
        },
        'SI-07SP:ID-VPU29':  {
            'polarizations': ('vertical', ),
            'pparameter': None,
            'kparameter': 'SI-07SP:ID-VPU29:KParam-Mon',
            IDFF_CC_LABELS[0]: 'SI-07SP:PS-CC1-1:Current-SP',  # upstream
            IDFF_CC_LABELS[1]: 'SI-07SP:PS-CC2-1:Current-SP',  # upstream
            IDFF_CC_LABELS[2]: 'SI-07SP:PS-CC1-2:Current-SP',  # downstream
            IDFF_CC_LABELS[3]: 'SI-07SP:PS-CC2-2:Current-SP',  # downstream

        },
        'SI-08SB:ID-IVU18': {
            'polarizations': ('horizontal', ),
            'pparameter': None,
            'kparameter': 'SI-08SB:ID-IVU18:KParam-Mon',
            IDFF_CH_LABELS[0]: 'SI-08SB:PS-CH-1:Current-SP',  # upstream
            IDFF_CH_LABELS[1]: 'SI-08SB:PS-CH-2:Current-SP',  # downstream
            IDFF_CV_LABELS[0]: 'SI-08SB:PS-CV-1:Current-SP',
            IDFF_CV_LABELS[1]: 'SI-08SB:PS-CV-2:Current-SP',
            IDFF_QS_LABELS[0]: 'SI-08M1:PS-QS:Current-SP',
            IDFF_QS_LABELS[1]: 'SI-08M2:PS-QS:Current-SP',
            IDFF_LC_LABELS[0]: 'SI-08SB:PS-LCH:Current-SP',
            IDFF_QN_LABELS[0]: 'SI-08M1:PS-QDB1:Current-SP',
            IDFF_QN_LABELS[1]: 'SI-08M1:PS-QFB:Current-SP',
            IDFF_QN_LABELS[2]: 'SI-08M1:PS-QDB2:Current-SP',
            IDFF_QN_LABELS[3]: 'SI-08M2:PS-QDB2:Current-SP',
            IDFF_QN_LABELS[4]: 'SI-08M2:PS-QFB:Current-SP',
            IDFF_QN_LABELS[5]: 'SI-08M2:PS-QDB1:Current-SP',
            'offsets': [
                IDFF_QN_LABELS[0], IDFF_QN_LABELS[1], IDFF_QN_LABELS[2],
                IDFF_QN_LABELS[3], IDFF_QN_LABELS[4], IDFF_QN_LABELS[5],
            ],  # [A]
        },
        'SI-09SA:ID-APU22': None,
        'SI-10SB:ID-EPU50': {
            'polarizations': tuple(
                item[0] for item in
                _idname2pol_sts['SI-10SB:ID-EPU50'].values()),
            'pparameter': 'SI-10SB:ID-EPU50:Phase-Mon',
            'kparameter': 'SI-10SB:ID-EPU50:Gap-Mon',
            IDFF_CH_LABELS[0]: 'SI-10SB:PS-CH-1:Current-SP',  # upstream
            IDFF_CH_LABELS[1]: 'SI-10SB:PS-CH-2:Current-SP',  # downstream
            IDFF_CV_LABELS[0]: 'SI-10SB:PS-CV-1:Current-SP',
            IDFF_CV_LABELS[1]: 'SI-10SB:PS-CV-2:Current-SP',
            IDFF_QS_LABELS[0]: 'SI-10SB:PS-QS-1:Current-SP',
            IDFF_QS_LABELS[1]: 'SI-10SB:PS-QS-2:Current-SP',
        },
        'SI-10SB:ID-DELTA52': {
            'polarizations': tuple(
                item[0] for item in
                _idname2pol_sts['SI-10SB:ID-DELTA52'].values()),
            'pparameter': 'SI-10SB:ID-DELTA52:PParam-Mon',
            'kparameter': 'SI-10SB:ID-DELTA52:KParam-Mon',
            IDFF_CH_LABELS[0]: 'SI-10SB:PS-CH-1:Current-SP',  # upstream
            IDFF_CH_LABELS[1]: 'SI-10SB:PS-CH-2:Current-SP',  # downstream
            IDFF_CV_LABELS[0]: 'SI-10SB:PS-CV-1:Current-SP',
            IDFF_CV_LABELS[1]: 'SI-10SB:PS-CV-2:Current-SP',
            IDFF_QS_LABELS[0]: 'SI-10SB:PS-QS-1:Current-SP',
            IDFF_QS_LABELS[1]: 'SI-10SB:PS-QS-2:Current-SP',
        },
        'SI-11SP:ID-UE44': {
            'polarizations': tuple(
                item[0] for item in
                _idname2pol_sts['SI-11SP:ID-UE44'].values()),
            'pparameter': 'SI-11SP:ID-UE44:PParam-Mon',
            'kparameter': 'SI-11SP:ID-UE44:KParam-Mon',
            IDFF_CH_LABELS[0]: 'SI-11SP:PS-CH-1:Current-SP',  # upstream
            IDFF_CH_LABELS[1]: 'SI-11SP:PS-CH-2:Current-SP',  # downstream
            IDFF_CV_LABELS[0]: 'SI-11SP:PS-CV-1:Current-SP',
            IDFF_CV_LABELS[1]: 'SI-11SP:PS-CV-2:Current-SP',
            IDFF_QS_LABELS[0]: 'SI-11SP:PS-QS-1:Current-SP',
            IDFF_QS_LABELS[1]: 'SI-11SP:PS-QS-2:Current-SP',
            IDFF_LC_LABELS[0]: 'SI-11SP:PS-LCH-1:Current-SP',
            IDFF_LC_LABELS[1]: 'SI-11SP:PS-LCV-1:Current-SP',
            IDFF_LC_LABELS[2]: 'SI-11SP:PS-LCV-2:Current-SP',
            },
        'SI-14SB:ID-IVU18': {
            'polarizations': ('horizontal', ),
            'pparameter': None,
            'kparameter': 'SI-14SB:ID-IVU18:KParam-Mon',
            IDFF_CH_LABELS[0]: 'SI-14SB:PS-CH-1:Current-SP',  # upstream
            IDFF_CH_LABELS[1]: 'SI-14SB:PS-CH-2:Current-SP',  # downstream
            IDFF_CV_LABELS[0]: 'SI-14SB:PS-CV-1:Current-SP',
            IDFF_CV_LABELS[1]: 'SI-14SB:PS-CV-2:Current-SP',
            IDFF_QS_LABELS[0]: 'SI-14M1:PS-QS:Current-SP',
            IDFF_QS_LABELS[1]: 'SI-14M2:PS-QS:Current-SP',
            IDFF_LC_LABELS[0]: 'SI-14SB:PS-LCH:Current-SP',
            IDFF_QN_LABELS[0]: 'SI-14M1:PS-QDB1:Current-SP',
            IDFF_QN_LABELS[1]: 'SI-14M1:PS-QFB:Current-SP',
            IDFF_QN_LABELS[2]: 'SI-14M1:PS-QDB2:Current-SP',
            IDFF_QN_LABELS[3]: 'SI-14M2:PS-QDB2:Current-SP',
            IDFF_QN_LABELS[4]: 'SI-14M2:PS-QFB:Current-SP',
            IDFF_QN_LABELS[5]: 'SI-14M2:PS-QDB1:Current-SP',
            'offsets': [
                IDFF_QN_LABELS[0], IDFF_QN_LABELS[1], IDFF_QN_LABELS[2],
                IDFF_QN_LABELS[3], IDFF_QN_LABELS[4], IDFF_QN_LABELS[5],
            ],  # [A]
        },
        'SI-17SA:ID-APU22': {
            'polarizations': ('horizontal', ),
            'pparameter': None,
            'kparameter': 'SI-17SA:ID-APU22:Phase-Mon',
            IDFF_CH_LABELS[0]: 'SI-17SA:PS-CH-1:Current-SP',  # upstream
            IDFF_CH_LABELS[1]: 'SI-17SA:PS-CH-2:Current-SP',  # downstream
            IDFF_CV_LABELS[0]: 'SI-17SA:PS-CV-1:Current-SP',
            IDFF_CV_LABELS[1]: 'SI-17SA:PS-CV-2:Current-SP',
        },
    }

    _idnames_list = list()

    _idtype_dict = dict()
    _idtype_2_idnames_dict = dict()
    _idtype_2_excdat_dict = dict()
    _idname_2_idmodel_dict = dict()
    _idmodel_2_idname_dict = dict()

    _lock = _Lock()

    @staticmethod
    def get_idnames(filters=None):
        """Return a sorted and filtered list of all ID names."""
        idnames_list = list(IDSearch._idname_2_idff.keys())
        idnames = _Filter.process_filters(idnames_list, filters=filters)
        return sorted(idnames)

    @staticmethod
    def get_idtype_names():
        """Return sorted list of insertion device types."""
        with IDSearch._lock:
            IDSearch._reload_idtype_dict()
        return sorted(set(IDSearch._idtype_dict.keys()))

    @staticmethod
    def get_idmodel_names():
        """Return sorted list of insertion device models."""
        IDSearch._reload_idname_2_idmodel_dict()
        return sorted(set(IDSearch._idmodel_2_idname_dict.keys()))

    @staticmethod
    def get_idtype_dict():
        """Return idtype dictionary.

        With key,value pairs of insertion device types and corresponding
        (polarities,mag_function).
        """
        with IDSearch._lock:
            IDSearch._reload_idtype_dict()
        return _copy.deepcopy(IDSearch._idtype_dict)

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
    def conv_idname_2_idff_offsets_labels(idname):
        """."""
        idff = IDSearch._idname_2_idff[idname]
        if idff is None or 'offsets' not in idff:
            return list()
        else:
            return idff['offsets']

    @staticmethod
    def conv_idname_2_idff_chnames(idname):
        """."""
        return IDSearch.conv_idname_labels_2_corrnames(
            idname, IDSearch.IDFF_CH_LABELS)

    @staticmethod
    def conv_idname_2_idff_cvnames(idname):
        """."""
        return IDSearch.conv_idname_labels_2_corrnames(
            idname, IDSearch.IDFF_CV_LABELS)

    @staticmethod
    def conv_idname_2_idff_qsnames(idname):
        """."""
        return IDSearch.conv_idname_labels_2_corrnames(
            idname, IDSearch.IDFF_QS_LABELS)

    @staticmethod
    def conv_idname_2_idff_lcnames(idname):
        """."""
        return IDSearch.conv_idname_labels_2_corrnames(
            idname, IDSearch.IDFF_LC_LABELS)

    @staticmethod
    def conv_idname_2_idff_qnnames(idname):
        """."""
        return IDSearch.conv_idname_labels_2_corrnames(
            idname, IDSearch.IDFF_QN_LABELS)

    @staticmethod
    def conv_idname_2_idff_ccnames(idname):
        """."""
        return IDSearch.conv_idname_labels_2_corrnames(
            idname, IDSearch.IDFF_CC_LABELS)

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
        pols_sts = IDSearch._idname2pol_sts[idname]
        if len(pols_sts) == 1:
            return next(iter(pols_sts))

        params = IDSearch.conv_idname_2_parameters(idname)

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

    @staticmethod
    def conv_idname_labels_2_corrnames(idname, correctors):
        """Return correctors names from idname and corrector labels."""
        corrs = list()
        idff = IDSearch.conv_idname_2_idff(idname)
        if idff is None:
            return corrs
        for corr in correctors:
            if corr in idff:
                pvname = _SiriusPVName(idff[corr])
                corrs.append(pvname.device_name)
        return corrs

    @staticmethod
    def conv_idname_2_idtype(idname):
        """Return the ID type of a given insetion device name."""
        IDSearch._reload_idtype_2_idnames_dict()
        for idtype, idnames in IDSearch._idtype_2_idnames_dict.items():
            if idname in idnames:
                return idtype
        raise KeyError('Invalid idname "' + idname + '"!')

    @staticmethod
    def conv_idname_2_excdata(idname, polarization):
        """Convert psname to excdata."""
        idtype = IDSearch.conv_idname_2_idtype(idname)
        idtype_pol = idtype + '-' + polarization
        IDSearch._reload_idtype_2_excdat_dict(idtype_pol)
        return IDSearch._idtype_2_excdat_dict[idtype_pol]

    # --- private methods ---

    @staticmethod
    def _reload_idtype_dict():
        """Reload id type dictionary from web server."""
        if IDSearch._idtype_dict:
            return
        if not _web.server_online():
            raise Exception('could not read idtypes from web server!')
        text = _web.id_idtypes_names_read()
        data, _ = _util.read_text_data(text)
        idtype_dict = dict()
        for datum in data:
            name, polarity, magfunc = datum[0], datum[1], datum[2]
            idtype_dict[name] = (polarity, magfunc)
        IDSearch._idtype_dict = idtype_dict

    @staticmethod
    def _reload_idtype_2_idnames_dict():
        """Reload id type to insertion device names dictionary."""
        with IDSearch._lock:
            if IDSearch._idtype_2_idnames_dict:
                return
            IDSearch._reload_idtype_dict()
            idtypes = sorted(set(IDSearch._idtype_dict.keys()))
            idtype_2_idnames_dict = dict()
            idnames_list = list()
            for idtype in idtypes:
                text = _web.id_idtype_data_read(idtype + '.txt')
                data, _ = _util.read_text_data(text)
                idnames = [_SiriusPVName(datum[0]) for datum in data]
                idtype_2_idnames_dict[idtype] = idnames
                idnames_list += idnames
            IDSearch._idtype_2_idnames_dict = idtype_2_idnames_dict
            IDSearch._idnames_list = sorted(idnames_list)

    @staticmethod
    def _reload_idtype_2_excdat_dict(idtype_pol):
        """Load ID conversion data."""
        with IDSearch._lock:
            if idtype_pol in IDSearch._idtype_2_excdat_dict:
                return
            if not _web.server_online():
                raise Exception(
                    'could not read "' + str(idtype_pol) + '" from web server!'
                )
            IDSearch._idtype_2_excdat_dict[idtype_pol] = _ExcitationData(
                filename_web=idtype_pol + '.txt'
            )

    @staticmethod
    def _reload_idname_2_idmodel_dict():
        """Load idmodels by idname to a dict."""
        with IDSearch._lock:
            if IDSearch._idname_2_idmodel_dict:
                return
            if not _web.server_online():
                raise Exception('could not read idmodels from web server')
            id_data, _ = _util.read_text_data(_web.id_idmodels_read())
            data = id_data
            idname_2_idmodel_dict = dict()
            idmodel_2_idname_dict = dict()
            for datum in data:
                idname, idmodel = datum
                idname_2_idmodel_dict[idname] = idmodel
                if idmodel not in idmodel_2_idname_dict:
                    idmodel_2_idname_dict[idmodel] = list()
                idmodel_2_idname_dict[idmodel].append(idname)
            IDSearch._idname_2_idmodel_dict = idname_2_idmodel_dict
            IDSearch._idmodel_2_idname_dict = idmodel_2_idname_dict
