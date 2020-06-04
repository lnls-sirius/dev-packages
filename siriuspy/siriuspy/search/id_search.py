"""Search module."""


class IDSearch:
    """ID Search Class."""

    _beamline2idname = {
        'CARNAUBA': 'SI-06SB:ID-Delta21',
        'CATERETE': 'SI-07SP:ID-Delta21',
        'EMA':      'SI-08SB:ID-APU19',
        'MANACA':   'SI-09SA:ID-APU22',
        'SABIA':    'SI-10SB:ID-Delta52',
        'IPE':      'SI-11SP:ID-Delta52',
        'COLIBRI':  'SI-12SB:ID-Delta52',
        'HARPIA':   'SI-14SB:ID-Delta21',
        'SAGUI':    'SI-15SP:ID-Delta21',
        'INGA':     'SI-16SB:ID-Delta21',
        'SAPUCAIA': 'SI-17SA:ID-APU19',
        'PAINEIRA': 'SI-18SB:ID-Delta21',
    }
    _idname2beamline = {v: k for k, v in _beamline2idname.items()}

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
