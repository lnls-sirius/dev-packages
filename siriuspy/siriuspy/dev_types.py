# This module contains data that should be in accordance with databases in the CCDB
# Ideally this module should consume online data from the CCDB service, instead of replicating
# it here. Implementation needed !!!

# this should replicate info in the CCDB machine application

from siriuspy.namedtuple import EnumTypes as _EnumTypes
from siriuspy.namedtuple import PVDB as _PVDB
from siriuspy.namedtuple import PSLimitsAll as _PSLimitsAll
from siriuspy.namedtuple import PSLimits as _PSLimits

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


"""Named tuple with all power supply limits"""
ps_limits_all = _PSLimitsAll(
    si_quad_q14_fam = _PSLimits(name='si-quadrupole-q14-fam', lo=0.0, hi=120.0),
    si_quad_q20_fam = _PSLimits(name='si-quadrupole-q20-fam', lo=0.0, hi=120.0),
    si_quad_q30_fam = _PSLimits(name='si-quadrupole-q30-fam', lo=0.0, hi=120.0),
    )


"""Generic magnet power supply"""
dev_ps_magnet = (
    _PVDB(name='Reset-Cmd',    type='int',   value=0),
    _PVDB(name='CtrlMode-Mon', type='enum',  enums=enum_types.RmtLocTyp, value=enum_types.RmtLocTyp.index('Remote')),
    _PVDB(name='PwrState-Sel', type='enum',  enums=enum_types.OffOnTyp,  value=enum_types.OffOnTyp.index('On')),
    _PVDB(name='PwrState-Sts', type='enum',  enums=enum_types.OffOnTyp,  value=enum_types.OffOnTyp.index('On')),
    _PVDB(name='OpMode-Sel',   type='enum',  enums=enum_types.PSOpModeTyp,  value=enum_types.PSOpModeTyp.index('SlowRef')),
    _PVDB(name='OpMode-Sts',   type='enum',  enums=enum_types.PSOpModeTyp,  value=enum_types.PSOpModeTyp.index('SlowRef')),
    _PVDB(name='Current-SP',   type='float', value=0.0, prec=4, unit='A'),
    _PVDB(name='Current-RB',   type='float', value=0.0, prec=4, unit='A'),)

"""SI quadrupole Q14 power supply"""
_ps_limits = ps_limits_all.si_quad_q14_fam
si_quad_q14_fam = dev_ps_magnet + (
    _PVDB(name='Current-SP',   type='float', value=0.0, prec=4, unit='A'),
    _PVDB(name='Current-RB',   type='float', value=0.0, prec=4, unit='A', lo=_ps_limits.lo, hi=_ps_limits.hi),)

"""SI quadrupole Q20 power supply"""
_ps_limits = ps_limits_all.si_quad_q20_fam
si_quad_q20_fam = dev_ps_magnet + (
    _PVDB(name='Current-SP',   type='float', value=0.0, prec=4, unit='A'),
    _PVDB(name='Current-RB',   type='float', value=0.0, prec=4, unit='A', lo=_ps_limits.lo, hi=_ps_limits.hi),)



def get_device_database(dev):
    """Return a dictionary with the device PV database."""
    database = {}
    for prop in dev:
        database[prop.name] = prop._asdict()
    return database
