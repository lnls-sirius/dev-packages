"""Subpackage BSMP.

Basic Small Message protocol

Documentation:
http://git.cnpem.br/bruno.martins/libbsmp/raw/master/doc/protocol_v2.20_pt_BR.pdf
http://git.cnpem.br/bruno.martins/libbsmp/raw/master/doc/protocol_v2.20_en_US.pdf

"""

from .serial import *
from .types import *
from .entities import *
from .commands import *
from .exceptions import *


__version__ = '2.20.0'
del serial, types, entities, commands, exceptions
