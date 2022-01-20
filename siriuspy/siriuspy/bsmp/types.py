"""BSMP types definitions."""
import enum
import typing


@enum.unique
class BSMPBytesFmt(str, enum.Enum):
    CHAR = "<c"
    UCHAR = "<B"
    USHORT = "<H"
    UINT = "<I"
    FLOAT = "<f"


class BSMPType(typing.NamedTuple):
    type: str
    size: int
    fmt: str
    check: typing.Callable[[typing.Any], bool]


class Types:
    """Types used by BSMP entities."""

    T_CHAR = BSMPType("char", 1, BSMPBytesFmt.CHAR.value, lambda x: isinstance(x, str))
    T_UINT8 = BSMPType("uint8", 1, BSMPBytesFmt.UCHAR.value, lambda x: isinstance(x, int))
    T_UINT16 = BSMPType("uint16", 2, BSMPBytesFmt.USHORT.value, lambda x: isinstance(x, int))
    T_UINT32 = BSMPType("uint32", 4, BSMPBytesFmt.UINT.value, lambda x: isinstance(x, int))
    T_FLOAT = BSMPType("float", 4, BSMPBytesFmt.FLOAT.value, lambda x: isinstance(x, float))
    T_PARAM = BSMPType("uint16", 2, BSMPBytesFmt.USHORT.value, lambda x: isinstance(x, int))
    T_STATE = BSMPType("uint16", 2, BSMPBytesFmt.USHORT.value, lambda x: isinstance(x, int))
    T_ENUM = BSMPType("uint16", 2, BSMPBytesFmt.USHORT.value, lambda x: isinstance(x, int))
    T_DSP_CLASS = BSMPType("uint16", 2, BSMPBytesFmt.USHORT.value, lambda x: isinstance(x, int))
