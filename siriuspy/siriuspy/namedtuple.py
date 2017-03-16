
from collections import namedtuple as _namedtuple


# --- enum types ---

EnumTypes = _namedtuple('EnumTypes', ('OffOnTyp',
                                      'OffOnWaitTyp',
                                      'DsblEnblTyp',
                                      'PSOpModeTyp',
                                      'RmtLocTyp',
                                      'SOFBOpModeTyp',))


# --- properties databases ---

_DevicePropDB = _namedtuple('DevicePropDB', ('name',
                                             'type',
                                             'enums',
                                             'count',
                                             'value',
                                             'unit',
                                             'prec',
                                             'scan',
                                             'lolo',
                                             'lo',
                                             'lolim',
                                             'hilim',
                                             'high',
                                             'hihi'))

class DevicePropDB(_DevicePropDB):
    def __new__(cls, name, type,
                     enums=None,
                     count=1,
                     value=None,
                     unit='',
                     prec=None,
                     scan=None,
                     lolo=None,
                     lo=None,
                     lolim=None,
                     hilim=None,
                     hi=None,
                     hihi=None):
        return super().__new__(cls, name=name, type=type,
                                    enums=enums,
                                    count=count,
                                    value=value,
                                    unit=unit,
                                    prec=prec,
                                    scan=scan,
                                    lolo=lolo,
                                    lo=lo,
                                    lolim=lolim,
                                    hilim=hilim,
                                    hi=hi,
                                    hihi=hihi
                                    )
    def _asdict(self):
        d = {}
        for field in self._fields:
            if field != 'name':
                attr = self.__getattribute__(field)
                if attr is not None:
                    d[field] = self.__getattribute__(field)
        return d
