"""Definition of factories.

MagnetFacoty
    used to create magnets
"""
import re as _re

from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.magnet.model import MagnetPowerSupply as _MagnetPowerSupply
from siriuspy.magnet.model import MagnetPowerSupplyDipole as \
    _MagnetPowerSupplyDipole
from siriuspy.magnet.model import MagnetPowerSupplyTrim as \
    _MagnetPowerSupplyTrim
from siriuspy.pulsedma.model import PulsedMagnetPowerSupply as \
    _PulsedMagnetPowerSupply


class MagnetFactory:
    """Return a magnet object."""

    @staticmethod
    def factory(maname, use_vaca=True, vaca_prefix=None, lock=True):
        """Return the right magnet object given its name."""
        maname = _SiriusPVName(maname)
        pulsed_discipline = _re.compile("PM")
        dipole = _re.compile("B.*")
        trim = _re.compile("SI-\d{2}\w\d:MA-(QD|QF|Q\d).*")
        if pulsed_discipline.match(maname.discipline):
            return _PulsedMagnetPowerSupply(maname,
                                            use_vaca=use_vaca,
                                            vaca_prefix=vaca_prefix,
                                            lock=lock)
        elif dipole.match(maname.dev_type):
            return _MagnetPowerSupplyDipole(maname,
                                            use_vaca=use_vaca,
                                            vaca_prefix=vaca_prefix,
                                            lock=lock)
        elif trim.match(maname):
            return _MagnetPowerSupplyTrim(maname,
                                          use_vaca=use_vaca,
                                          vaca_prefix=vaca_prefix,
                                          lock=lock)
        else:
            return _MagnetPowerSupply(maname,
                                      use_vaca=use_vaca,
                                      vaca_prefix=vaca_prefix,
                                      lock=lock)
