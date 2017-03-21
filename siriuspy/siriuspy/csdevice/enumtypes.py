
class _ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class EnumTypes:

    _types = {
        'OffOnTyp'      : ('Off', 'On'),
        'OffOnWaitTyp'  : ('Off', 'On', 'Wait'),
        'DsblEnblTyp'   : ('Dsbl', 'Enbl'),
        'PSOpModeTyp'   : ('SlowRef', 'FastRef', 'WfmRef', 'SigGen'),
        'RmtLocTyp'     : ('Remote', 'Local'),
        'SOFBOpModeTyp' : ('Off', 'AutoCorr', 'MeasRespMat'),
    }

    @staticmethod
    def enums(typ):
        if typ not in EnumTypes._types: return None
        return EnumTypes._types[typ]

    @staticmethod
    def idx(typ,value):
        values = EnumTypes.enums(typ)
        if value not in values: return None
        return values.index(value)

    @staticmethod
    def key(typ,idx):
        values = EnumTypes.enums(typ)
        return values[idx]

    @_ClassProperty
    @classmethod
    def names(cls):
        return tuple(cls._types.keys())
