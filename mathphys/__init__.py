"""Math functions, physical constants and auxiliary functions"""

import os as _os
import mathphys.base_units as base_units
import mathphys.units as units
import mathphys.constants as constants
import mathphys.functions as functions
import mathphys.beam_optics as beam_optics
import mathphys.beam_lifetime as beam_lifetime
import mathphys.utils as utils

__all__ = ['base_units', 'units', 'constants', 'functions', 'beam_optics',
    'beam_lifetime', 'utils']

with open(_os.path.join(__path__[0], 'VERSION'), 'r') as _f:
    __version__ = _f.read().strip()
