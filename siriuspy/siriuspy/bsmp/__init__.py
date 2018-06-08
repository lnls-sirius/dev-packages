"""Subpackage BSMP.

Basic Small Message protocol

Documentation:
https://github.com/lnls-sirius/libbsmp/blob/master/doc/protocol_v2-30_pt_BR.pdf
https://github.com/lnls-sirius/libbsmp/blob/master/doc/protocol_v2-30_en_US.pdf
"""

from .serial import *
from .types import *
from .entities import *
from .commands import *
from .exceptions import *


__version__ = '2.30.0'
del serial, types, entities, commands, exceptions
