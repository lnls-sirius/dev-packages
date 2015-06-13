"""Math functions, physical constants and auxilliary functions"""

import os as _os
import mathphys.base_units as base_units
import mathphys.units as units
import mathphys.constants as constants
import mathphys.functions as functions
import mathphys.beam_optics as beam_optics
import mathphys.beam_lifetime as beam_lifetime

__all__ = ['base_units', 'units','constants','functions','beam_optics']

with open(_os.path.join(__path__[0], 'VERSION'), 'r') as _f:
    __version__ = _f.read().strip()
