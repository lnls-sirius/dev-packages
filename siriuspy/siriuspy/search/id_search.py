"""Search module."""


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
