"""BSMP types definitions."""
from collections import namedtuple


class Types:
    """Types used by BSMP entities."""

    _BSMPType = namedtuple('BSMPType', 'type, size, fmt, check')

    t_none = _BSMPType(None, 0, None, lambda x: x is None)
    t_char = _BSMPType('char', 1, '<c', lambda x: isinstance(x, str))
    t_uint8 = _BSMPType('uint8', 1, '<B', lambda x: isinstance(x, int))
    t_uint16 = _BSMPType('uint16', 2, '<H', lambda x: isinstance(x, int))
    t_uint32 = _BSMPType('uint32', 4, '<I', lambda x: isinstance(x, int))
    t_float = _BSMPType('float', 4, '<f', lambda x: isinstance(x, float))
