
from collections import namedtuple as _namedtuple


_EnumTypes = _namedtuple('EnumTypes', ('OffOnTyp',
                                       'OffOnWaitTyp',
                                       'DsblEnblTyp',
                                       'PSOpModeTyp',
                                       'RmtLocTyp',
                                       'SOFBOpModeTyp',))


"""All enumeration types defined for devices"""
enum_types = _EnumTypes(
    OffOnTyp      = ('Off', 'On'),
    OffOnWaitTyp  = ('Off', 'On', 'Wait'),
    DsblEnblTyp   = ('Dsbl', 'Enbl'),
    PSOpModeTyp   = ('SlowRef', 'FastRef', 'WfmRef', 'SigGen'),
    RmtLocTyp     = ('Remote', 'Local'),
    SOFBOpModeTyp = ('Off', 'AutoCorr', 'MeasRespMat'),)
