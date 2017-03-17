
from collections import namedtuple as _namedtuple


# --- enum types ---

EnumTypes = _namedtuple('EnumTypes', ('OffOnTyp',
                                      'OffOnWaitTyp',
                                      'DsblEnblTyp',
                                      'PSOpModeTyp',
                                      'RmtLocTyp',
                                      'SOFBOpModeTyp',))


# --- PS parameters ---

_PSLimits = _namedtuple('PSLimits', ('name',
                                     'lolo',
                                     'lo',
                                     'lolim',
                                     'hilim',
                                     'hi',
                                     'hihi',))

class PSLimits(_PSLimits):
    def __new__(cls, name,
                     lolo=None,
                     lo=None,
                     lolim=None,
                     hilim=None,
                     hi=None,
                     hihi=None):
        return super().__new__(cls, name=name,
                                    lolo=lolo,
                                    lo=lo,
                                    lolim=lolim,
                                    hilim=hilim,
                                    hi=hi,
                                    hihi=hihi)
    def _asdict(self):
        d = {}
        for field in self._fields:
            if field != 'name':
                attr = self.__getattribute__(field)
                if attr is not None:
                    d[field] = self.__getattribute__(field)
        return d

PSLimitsAll = _namedtuple('AllPSLimits', ('si_quad_q14_fam',
                                          'si_quad_q20_fam',
                                          'si_quad_q30_fam',))


# --- PV database ---

_PVDB = _namedtuple('DevicePropDB', ('name',
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
                                     'hi',
                                     'hihi'))

class PVDB(_PVDB):
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
