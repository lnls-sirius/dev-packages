
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
                                             'scan',))

class DevicePropDB(_DevicePropDB):
    def __new__(cls, name, type,
                     enums=None,
                     count=1,
                     value=None,
                     unit='',
                     prec=None,
                     scan=None):
        return super().__new__(cls, name=name, type=type,
                                    enums=enums,
                                    count=count,
                                    value=value,
                                    unit=unit,
                                    prec=prec,
                                    scan=scan)
