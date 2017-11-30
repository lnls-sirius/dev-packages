"""Enumtypes module."""

import types as _types
import copy as _copy


class _ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class EnumTypes:
    """EnumTypes Class."""

    # This should be constructed from CCDB server.

    _types_general = {
        'OffOnTyp': ('Off', 'On'),
        'OffOnWaitTyp': ('Off', 'On', 'Wait'),
        'DsblEnblTyp': ('Dsbl', 'Enbl'),
        'RmtLocTyp': ('Remote', 'Local'),
    }

    _types_ps = {
        'PSOpModeTyp': ('SlowRef', 'SlowRefSync', 'FastRef',
                        'RmpWfm', 'MigWfm', 'Cycle'),
        'PSWfmLabelsTyp': ('Waveform1', 'Waveform2', 'Waveform3',
                           'Waveform4', 'Waveform5', 'Waveform6'),
        'PSIntlkLabelsTyp': ('Bit0', 'Bit1', 'Bit2', 'Bit3',
                             'Bit4', 'Bit5', 'Bit6', 'Bit7'),
    }

    _types_sofb = {
        'SOFBOpModeTyp': ('Off', 'AutoCorr', 'MeasRespMat'),
    }

    _types = {}
    _types.update(_types_general)
    _types.update(_types_ps)
    _types.update(_types_sofb)

    @staticmethod
    def enums(typ):
        """Return enum values of a given enumerate type."""
        if typ not in EnumTypes._types:
            return None
        return EnumTypes._types[typ]

    @staticmethod
    def get_idx(typ, value):
        """Return enumerate index of a given value of a given enum mtype."""
        values = EnumTypes.enums(typ)
        if value not in values:
            return None
        return values.index(value)

    @staticmethod
    def key(typ, idx):
        """Return enumerate value corresponding to a given index and type."""
        if idx is None:
            return 'None'
        values = EnumTypes.enums(typ)
        return values[idx]

    @staticmethod
    def values(typ):
        """Return valid index list of a given enumerate type."""
        return tuple(range(len(EnumTypes._types[typ])))

    @staticmethod
    def types():
        """Return a copy of the enumerate types dictionary."""
        return _copy.deepcopy(EnumTypes._types)

    @_ClassProperty
    @classmethod
    def names(cls):
        """Return names of all defined enumerate types."""
        return tuple(cls._types.keys())


# create class attribute 'idx' object with all constants
EnumTypes.idx = _types.SimpleNamespace()
for k, v in EnumTypes._types.items():
    for i in range(len(v)):
        setattr(EnumTypes.idx, v[i], i)
del(k, v, i)
