"""ID Search module."""

from threading import Lock as _Lock

from .. import clientweb as _web
from ..magnet.excdata import ExcitationData as _ExcitationData

from .ps_search import PSSearch as _PSSearch


class IDSearch:
    """ID Search Class."""

    _beamline2subsection = {
        'Carnauba': '06SB',
        'Caterete': '07SP',
        'Ema': '08SB',
        'Manaca': '09SA',
        'Sabia': '10SB',
        'Ipe': '11SP',
        'PGM++': '12SB',
    }
    _subsection2beamline = {v: k for k, v in _beamline2subsection.items()}

    _idname_2_orbitcorr = {
        'SI-09SA:ID-APU22': (
            'SI-09SA:PS-CH-1', 'SI-09SA:PS-CH-2',
            'SI-09SA:PS-CH-3', 'SI-09SA:PS-CH-4',
            'SI-09SA:PS-CV-1', 'SI-09SA:PS-CV-2',
            'SI-09SA:PS-CV-3', 'SI-09SA:PS-CV-4',
        )
    }

    _idname_2_orbitffwd_fname = {
        'SI-09SA:ID-APU22': 'si-id-apu22-ffwd-09sa',
    }

    _idname_2_orbitffwd_dict = dict()

    _lock = _Lock()

    @staticmethod
    def conv_subsection_2_beamline(subsection):
        """Return the beam line name corresponding to sector."""
        if subsection in IDSearch._subsection2beamline.keys():
            return IDSearch._subsection2beamline[subsection]
        return None

    @staticmethod
    def conv_beamline_2_subsection(beamline):
        """Return the beam line name corresponding to subsection."""
        if beamline in IDSearch._beamline2subsection.keys():
            return IDSearch._beamline2subsection[beamline]
        return None

    @staticmethod
    def get_subsection_2_beamline_dict():
        """Return subsection to beamline dictionary."""
        return IDSearch._subsection2beamline.copy()

    @staticmethod
    def get_beamline_2_subsection_dict():
        """Return beamline to subsection dictionary."""
        return IDSearch._beamline2subsection.copy()

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
        """Convert idname to orbit ffwd."""
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
            ffwd_fname = IDSearch._idname_2_orbitffwd_fname[idname]
            IDSearch._idname_2_orbitffwd_dict[idname] = \
                _ExcitationData(filename_web=ffwd_fname + '.txt')
