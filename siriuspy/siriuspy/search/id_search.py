"""ID Search module."""

from threading import Lock as _Lock

from .. import clientweb as _web
from ..magnet.excdata import ExcitationData as _ExcitationData

from .ps_search import PSSearch as _PSSearch


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
        'SABIA':    'SI-10SB:ID-Delta52',
        # 'SABIA':    'SI-10SB:ID-EPU50',
        'IPE':      'SI-11SP:ID-APU58',
        'PAINEIRA': 'SI-14SB:ID-WIG180',
        # 'SAPUCAIA': 'SI-17SA:ID-???',
    }
    _idname2beamline = {v: k for k, v in _beamline2idname.items()}

    # NOTE: sorted according to lattice ordering: all upstream first,
    # and downstream correctors.
    # NOTE: should we separate dicts for horizontal and vertical corrs ?

    _idname_2_orbitcorr = {
        # 'SI-10SB:ID-EPU50': [
        #     'SI-10SB:PS-CH-1', 'SI-14SB:PS-CV-1',  # upstream
        #     'SI-10SB:PS-CH-2', 'SI-14SB:PS-CV-2',  # downstream
        #     ],
        'SI-14SB:ID-WIG180': [
            'SI-14SB:PS-CH-1',  # upstream
            'SI-14SB:PS-CH-2',  # downstream
            ],
    }

    _idname_2_orbitffwd_fname = {
        'SI-14SB:ID-WIG180': {
            'horizontal': {  # unique light horizontal polarizatipon
                'SI-14SB:PS-CH-1': 'si-wig180-ffwd-ch-1',
                'SI-14SB:PS-CH-2': 'si-wig180-ffwd-ch-2',
                },
        },
    }

    _idname_2_orbitffwd_dict = dict()

    _lock = _Lock()

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
    def get_idnames(filters=None):
        """Return a sorted and filtered list of all ID names."""
        filters_ = dict()
        if filters:
            filters_.update(filters)
        filters_['dis'] = 'ID'
        return _PSSearch.get_psnames(filters_)

    @staticmethod
    def conv_idname_2_orbitcorr(idname):
        """Return list of orbit correctors of a given ID."""
        return IDSearch._idname_2_orbitcorr[idname]

    @staticmethod
    def conv_idname_2_orbitffwd(idname):
        """Convert idname to orbit feedforward excdata."""
        IDSearch._reload_idname_2_orbitffwd_dict(idname)
        return IDSearch._idname_2_orbitffwd_dict[idname]

    # --- private methods ---

    @staticmethod
    def _reload_idname_2_orbitffwd_dict(idname):
        """Load ID ffwd data."""
        with IDSearch._lock:
            if idname in IDSearch._idname_2_orbitffwd_dict:
                return
            if not _web.server_online():
                raise Exception(
                    'could not read "' + str(idname) + '" from web server!')
            orbitffwd = dict()
            fnames_dict = IDSearch._idname_2_orbitffwd_fname[idname]
            for polarization, ffwd_fnames in fnames_dict.items():
                ps_excdata = dict()
                for psname, ffwd_fname in ffwd_fnames.items():
                    ps_excdata[psname] = \
                        _ExcitationData(filename_web=ffwd_fname + '.txt')
                orbitffwd[polarization] = ps_excdata
            IDSearch._idname_2_orbitffwd_dict[idname] = orbitffwd
