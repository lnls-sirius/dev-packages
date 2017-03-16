# This module contains data that should be in accordance with databases in the CCDB
# Ideally this module should consume online data from the CCDB service, instead of replicating
# it here. Implementation needed !!!

# this should replicate info in the CCDB machine application

from siriuspy.namedtuple import EnumTypes as _EnumTypes
from siriuspy.namedtuple import DevicePropDB as _DevicePropDB

# - Immutables should be used for static data structures to avoid corruption by package consumers
# - Named types should be used to allow for an easier code to read and use.

"""All enumeration types defined for devices"""
enum_types = _EnumTypes(
    OffOnTyp      = ('Off', 'On'),
    OffOnWaitTyp  = ('Off', 'On', 'Wait'),
    DsblEnblTyp   = ('Dsbl', 'Enbl'),
    PSOpModeTyp   = ('SlowRef', 'FastRef', 'WfmRef', 'SigGen'),
    RmtLocTyp     = ('Remote', 'Local'),
    SOFBOpModeTyp = ('Off', 'AutoCorr', 'MeasRespMat'),)


"""Generic magnet power supply"""
dev_ps_magnet = (
    _DevicePropDB(name='Reset-Cmd',    type='int',   value=0),
    _DevicePropDB(name='CtrlMode-Mon', type='enum',  enums=enum_types.RmtLocTyp, value=enum_types.RmtLocTyp.index('Remote')),
    _DevicePropDB(name='PwrState-Sel', type='enum',  enums=enum_types.OffOnTyp,  value=enum_types.OffOnTyp.index('On')),
    _DevicePropDB(name='PwrState-Sts', type='enum',  enums=enum_types.OffOnTyp,  value=enum_types.OffOnTyp.index('On')),
    _DevicePropDB(name='OpMode-Sel',   type='enum',  enums=enum_types.PSOpModeTyp,  value=enum_types.PSOpModeTyp.index('SlowRef')),
    _DevicePropDB(name='OpMode-Sts',   type='enum',  enums=enum_types.PSOpModeTyp,  value=enum_types.PSOpModeTyp.index('SlowRef')),
    _DevicePropDB(name='Current-SP',   type='float', value=0.0, prec=4, unit='A'),
    _DevicePropDB(name='Current-RB',   type='float', value=0.0, prec=4, unit='A'),)


def get_device_database(dev):
    """Return a dictionary with the device PV database."""
    database = {}
    for prop in dev:
        database[prop.name] = prop._asdict()
    return database
