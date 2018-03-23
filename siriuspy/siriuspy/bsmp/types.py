"""BSMP types definitions."""
from collections import namedtuple


class Types:
    """Types used by BSMP entities."""

    BSMPType = namedtuple('BSMPType', 'type, size, fmt, check')

    t_char = BSMPType('char', 1, '<c', lambda x: isinstance(x, str))
    t_uint8 = BSMPType('uint8', 1, '<B', lambda x: isinstance(x, int))
    t_uint16 = BSMPType('uint16', 2, '<H', lambda x: isinstance(x, int))
    t_uint32 = BSMPType('uint32', 4, '<I', lambda x: isinstance(x, int))
    t_float = BSMPType('float', 4, '<f', lambda x: isinstance(x, float))
