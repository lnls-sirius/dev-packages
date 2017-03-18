
from siriuspy.cs_device.enumtypes import enum_types as _enumt
from siriuspy.cs_device.pvdb import PVDB as _PVDB
from siriuspy.power_supply.psdata import get_ps_data as _get_ps_data


# PSData object with all PS properties
_psdata = _get_ps_data()


def _getdatabase(cls):
    if 'get_database' in dir(super(cls)):
        database = super(cls).get_database()
    else:
        database = {}
    for attr_name in dir(cls):
        attr_value = getattr(cls, attr_name)
        if type(attr_value) is _PVDB:
            database[attr_value.name] = attr_value._asdict()
    return database


class MagnetPSClasses:
    """Magnet Power Supply Classes"""

    class _Base:
        _Reset_Cmd    = _PVDB(name='Reset-Cmd',    type='int',   value=0)
        _CtrlMode_Mon = _PVDB(name='CtrlMode-Mon', type='enum',  enums=_enumt.RmtLocTyp,   value=_enumt.RmtLocTyp.index('Remote'))
        _PwrState_Sel = _PVDB(name='PwrState-Sel', type='enum',  enums=_enumt.OffOnTyp,    value=_enumt.OffOnTyp.index('On'))
        _PwrState_Sts = _PVDB(name='PwrState-Sts', type='enum',  enums=_enumt.OffOnTyp,    value=_enumt.OffOnTyp.index('On'))
        _OpMode_Sel   = _PVDB(name='OpMode-Sel',   type='enum',  enums=_enumt.PSOpModeTyp, value=_enumt.PSOpModeTyp.index('SlowRef'))
        _OpMode_Sts   = _PVDB(name='OpMode-Sts',   type='enum',  enums=_enumt.PSOpModeTyp, value=_enumt.PSOpModeTyp.index('SlowRef'))
        @staticmethod
        def get_database(): return _getdatabase(__class__)

    class si_quadrupole_q14_fam(_Base):
        """SI quadrupole Q14 power supply"""

        name = 'si-quadrupole-q14-fam'
        _Current_RB = _PVDB(name='Current-RB', type='float', value=0.0, prec=4, unit='A')
        _Current_SP = _PVDB(name='Current-SP', type='float', value=0.0, prec=4, unit='A',
                            lolim=_psdata.get_setpoint_limits(name, 'LOPR'),
                            hilim=_psdata.get_setpoint_limits(name, 'HOPR')
                           )
        @staticmethod
        def get_database(): return _getdatabase(__class__)

    class si_quadrupole_q20_fam(_Base):
        """SI quadrupole Q20 power supply"""

        name = 'si-quadrupole-q20-fam'
        _Current_RB = _PVDB(name='Current-RB', type='float', value=0.0, prec=4, unit='A')
        _Current_SP = _PVDB(name='Current-SP', type='float', value=0.0, prec=4, unit='A',
                            lolim=_psdata.get_setpoint_limits(name, 'LOPR'),
                            hilim=_psdata.get_setpoint_limits(name, 'HOPR')
                           )
        @staticmethod
        def get_database(): return _getdatabase(__class__)

    class si_quadrupole_q30_fam(_Base):
        """SI quadrupole Q30 power supply"""

        name = 'si-quadrupole-q30-fam'
        _Current_RB = _PVDB(name='Current-RB', type='float', value=0.0, prec=4, unit='A')
        _Current_SP = _PVDB(name='Current-SP', type='float', value=0.0, prec=4, unit='A',
                            lolim=_psdata.get_setpoint_limits(name, 'LOPR'),
                            hilim=_psdata.get_setpoint_limits(name, 'HOPR')
                           )
        @staticmethod
        def get_database(): return _getdatabase(__class__)


_pstypename2class = {
        'si-quadrupole-q14-fam' : MagnetPSClasses.si_quadrupole_q14_fam,
        'si-quadrupole-q20-fam' : MagnetPSClasses.si_quadrupole_q20_fam,
        'si-quadrupole-q30-fam' : MagnetPSClasses.si_quadrupole_q30_fam,
}

def get_psclass(pstype_name):
    """Return a reference to the magnte power supply class of a given name of
    a power supply type.
    """
    return _pstypename2class[pstype_name]
