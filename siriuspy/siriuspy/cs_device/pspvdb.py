
from siriuspy.cs_device.enumtypes import enum_types as _enumt
from siriuspy.cs_device.pvdb import PVDB as _PVDB
from siriuspy.power_supply.psdata import get_psdata as _get_psdata


# PSData object with all PS properties
_psdata = _get_psdata()


class MagPSPVDBClasses:
    """Magnet Power Supply PV Database Classes

    These classes define all PVs associated with each type of power supply.

    get_database(pstype_name):
        A static method that returns a pcaspy-style database dictionary with all
        properties that apply to the power supply type.

    get_classes():
        A static method of enclosing class MagPSPVDbClasses that returns the
        names of power supply types for which PVDV classes are defined. These
        names can be used with 'get_database'.
    """

    def _getdatabase(cls):
        """Auxilliary function for MagPSPVDB classes to return databases with
        all its PVDB properties."""
        if 'get_database' in dir(super(cls)):
            database = super(cls).get_database()
        else:
            database = {}
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if type(attr_value) is _PVDB:
                database[attr_value.name] = attr_value._asdict()
        return database

    class _Base:
        _Reset_Cmd    = _PVDB(name='Reset-Cmd',    type='int',   value=0)
        _CtrlMode_Mon = _PVDB(name='CtrlMode-Mon', type='enum',  enums=_enumt.RmtLocTyp,   value=_enumt.RmtLocTyp.index('Remote'))
        _PwrState_Sel = _PVDB(name='PwrState-Sel', type='enum',  enums=_enumt.OffOnTyp,    value=_enumt.OffOnTyp.index('On'))
        _PwrState_Sts = _PVDB(name='PwrState-Sts', type='enum',  enums=_enumt.OffOnTyp,    value=_enumt.OffOnTyp.index('On'))
        _OpMode_Sel   = _PVDB(name='OpMode-Sel',   type='enum',  enums=_enumt.PSOpModeTyp, value=_enumt.PSOpModeTyp.index('SlowRef'))
        _OpMode_Sts   = _PVDB(name='OpMode-Sts',   type='enum',  enums=_enumt.PSOpModeTyp, value=_enumt.PSOpModeTyp.index('SlowRef'))
        @staticmethod
        def get_database(): return MagPSPVDBClasses._getdatabase(__class__)

    class si_quadrupole_q14_fam(_Base):
        """SI quadrupole Q14 power supply"""

        name = 'si-quadrupole-q14-fam'
        _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
        _Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
                            lolo  =_psdata.get_setpoint_limits(name, 'LOLO'),
                            lo    =_psdata.get_setpoint_limits(name, 'LOW'),
                            lolim =_psdata.get_setpoint_limits(name, 'LOPR'),
                            hilim =_psdata.get_setpoint_limits(name, 'HOPR'),
                            hi    =_psdata.get_setpoint_limits(name, 'HIGH'),
                            hihi  =_psdata.get_setpoint_limits(name, 'HIHI'),
                           )
        @staticmethod
        def get_database(): return MagPSPVDBClasses._getdatabase(__class__)

    class si_quadrupole_q20_fam(_Base):
        """SI quadrupole Q20 power supply"""

        name = 'si-quadrupole-q20-fam'
        _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
        _Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
                            lolo  =_psdata.get_setpoint_limits(name, 'LOLO'),
                            lo    =_psdata.get_setpoint_limits(name, 'LOW'),
                            lolim =_psdata.get_setpoint_limits(name, 'LOPR'),
                            hilim =_psdata.get_setpoint_limits(name, 'HOPR'),
                            hi    =_psdata.get_setpoint_limits(name, 'HIGH'),
                            hihi  =_psdata.get_setpoint_limits(name, 'HIHI'),
                           )
        @staticmethod
        def get_database(): return MagPSPVDBClasses._getdatabase(__class__)

    class si_quadrupole_q30_fam(_Base):
        """SI quadrupole Q30 power supply"""

        name = 'si-quadrupole-q30-fam'
        _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
        _Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
                            lolo  =_psdata.get_setpoint_limits(name, 'LOLO'),
                            lo    =_psdata.get_setpoint_limits(name, 'LOW'),
                            lolim =_psdata.get_setpoint_limits(name, 'LOPR'),
                            hilim =_psdata.get_setpoint_limits(name, 'HOPR'),
                            hi    =_psdata.get_setpoint_limits(name, 'HIGH'),
                            hihi  =_psdata.get_setpoint_limits(name, 'HIHI'),
                           )
        @staticmethod
        def get_database(): return MagPSPVDBClasses._getdatabase(__class__)

    class si_sextupole_s15_ch(_Base):
        """SI sextupole S15 power supply for horizontal correctors"""

        name = 'si-sextupole-s15-ch'
        _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
        _Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
                            lolo  =_psdata.get_setpoint_limits(name, 'LOLO'),
                            lo    =_psdata.get_setpoint_limits(name, 'LOW'),
                            lolim =_psdata.get_setpoint_limits(name, 'LOPR'),
                            hilim =_psdata.get_setpoint_limits(name, 'HOPR'),
                            hi    =_psdata.get_setpoint_limits(name, 'HIGH'),
                            hihi  =_psdata.get_setpoint_limits(name, 'HIHI'),
                           )
        @staticmethod
        def get_database(): return MagPSPVDBClasses._getdatabase(__class__)

    @staticmethod
    def get_database(pstype_name):
        pstype_name = pstype_name.replace('-','_')
        if pstype_name in dir(__class__):
            return eval('MagPSPVDBClasses.' + pstype_name +'.get_database()')

    @staticmethod
    def get_classes():
        classes = []
        for method in dir(__class__):
            if method == '_Base': continue
            attr = getattr(__class__,method)
            if not isinstance(attr,type): continue
            if issubclass(getattr(__class__,method), MagPSPVDBClasses._Base):
                classes.append(method.replace('_','-'))
        return classes if classes else None


def get_database(pstype_name):
    """Return a pcaspy-style database dictionary with all properties that apply
    to the power supply type whose name is passed as an argument."""
    return MagPSPVDBClasses.get_database(pstype_name)

def get_classes():
    """List all power supply PVDV classes defined within MagPSPVDBClasses."""
    return MagPSPVDBClasses.get_classes()
