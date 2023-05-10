"""ID Search module."""

from ..namesys import Filter as _Filter
from ..namesys import SiriusPVName as _SiriusPVName


class IDSearch:
    """ID Search Class."""

    # NOTE: Maybe we should move these mappings to
    # static tables in our cs-constants server.

    # NOTE: see
    # https://wiki-sirius.lnls.br/mediawiki/index.php/Machine:Insertion_Devices

    _beamline2idname = {
        'CARNAUBA': 'SI-06SB:ID-APU22',
        'CATERETE': 'SI-07SP:ID-APU22',
        'EMA':      'SI-08SB:ID-APU22',
        'MANACA':   'SI-09SA:ID-APU22',
        'SABIA':    'SI-10SB:ID-EPU50',
        'IPE':      'SI-11SP:ID-APU58',
        'PAINEIRA': 'SI-14SB:ID-WIG180',
    }

    _idname2beamline = {v: k for k, v in _beamline2idname.items()}

    _idname_2_idff = {
        'SI-06SB:ID-APU22': None,
        'SI-07SP:ID-APU22': None,
        'SI-08SB:ID-APU22': None,
        'SI-09SA:ID-APU22': None,
        'SI-10SB:ID-EPU50': {
            'polarizations': (
                'none', 'circularn', 'horizontal', 'circularp', 'vertical',
                ),
            'pparameter': 'SI-10SB:ID-EPU50:Phase-Mon',
            'kparameter': 'SI-10SB:ID-EPU50:Gap-Mon',
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
    }

    @staticmethod
    def get_idnames(filters=None):
        """Return a sorted and filtered list of all ID names."""
        idnames_list = list(IDSearch._idname2beamline.keys())
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
    def conv_idname_2_idff(idname):
        """Return the IDFF dictionary for a given ID name."""
        return dict(IDSearch._idname_2_idff[idname])

    @staticmethod
    def conv_idname_2_pparameter_propty(idname):
        """."""
        idff = IDSearch.conv_idname_2_idff(idname)
        pvname = _SiriusPVName(idff['pparameter'])
        return pvname.propty

    @staticmethod
    def conv_idname_2_kparameter_propty(idname):
        """."""
        idff = IDSearch.conv_idname_2_idff(idname)
        pvname = _SiriusPVName(idff['kparameter'])
        return pvname.propty

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
        """Return ID light polarizations."""
        polarizations = IDSearch._idname_2_idff[idname]['polarizations']
        return polarizations

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
