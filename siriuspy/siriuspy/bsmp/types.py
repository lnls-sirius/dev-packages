"""BSMP types definitions."""
from collections import namedtuple


class Types:
    """Types used by BSMP entities."""

    _BSMPType = namedtuple('BSMPType', 'type, size, fmt, check')

    T_CHAR = _BSMPType('char', 1, '<c', lambda x: isinstance(x, str))
    T_UINT8 = _BSMPType('uint8', 1, '<B', lambda x: isinstance(x, int))
    T_UINT16 = _BSMPType('uint16', 2, '<H', lambda x: isinstance(x, int))
    T_UINT32 = _BSMPType('uint32', 4, '<I', lambda x: isinstance(x, int))
    T_FLOAT = _BSMPType('float', 4, '<f', lambda x: isinstance(x, float))
    T_PARAM = _BSMPType('uint16', 2, '<H', lambda x: isinstance(x, int))
    T_STATE = _BSMPType('uint16', 2, '<H', lambda x: isinstance(x, int))
    T_ENUM = _BSMPType('uint16', 2, '<H', lambda x: isinstance(x, int))
    T_DSP_CLASS = _BSMPType('uint16', 2, '<H', lambda x: isinstance(x, int))
