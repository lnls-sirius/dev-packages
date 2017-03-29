import copy as _copy
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.pwrsupply.psdata import get_setpoint_limits as _sp_limits


# PSData object with all PS properties
#_psdata = _get_psdata()

class PSClasses:
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
            if type(attr_value) is dict:
                d = _copy.deepcopy(attr_value)
                del d['name']
                database[attr_value['name']] = d
        return database

    class _Base:
        _Reset_Cmd    = {'name':'Reset-Cmd',    'type':'int',   'value':0}
        _CtrlMode_Mon = {'name':'CtrlMode-Mon', 'type':'enum',  'enums':_et.enums('RmtLocTyp'),   'value':_et.idx('RmtLocTyp', 'Remote')}
        _PwrState_Sel = {'name':'PwrState-Sel', 'type':'enum',  'enums':_et.enums('OffOnTyp'),    'value':_et.idx('OffOnTyp','On')}
        _PwrState_Sts = {'name':'PwrState-Sts', 'type':'enum',  'enums':_et.enums('OffOnTyp'),    'value':_et.idx('OffOnTyp','On')}
        _OpMode_Sel   = {'name':'OpMode-Sel',   'type':'enum',  'enums':_et.enums('PSOpModeTyp'), 'value':_et.idx('PSOpModeTyp','SlowRef')}
        _OpMode_Sts   = {'name':'OpMode-Sts',   'type':'enum',  'enums':_et.enums('PSOpModeTyp'), 'value':_et.idx('PSOpModeTyp','SlowRef')}
        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_quadrupole_q14_fam(_Base):
        """SI quadrupole Q14 power supply"""

        name = 'si-quadrupole-q14-fam'
        _Current_RB = {'name':'Current-RB','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        _Current_SP = {'name':'Current-SP','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_quadrupole_q20_fam(_Base):
        """SI quadrupole Q20 power supply"""

        name = 'si-quadrupole-q20-fam'
        _Current_RB = {'name':'Current-RB','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        _Current_SP = {'name':'Current-SP','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_quadrupole_q30_fam(_Base):
        """SI quadrupole Q30 power supply"""

        name = 'si-quadrupole-q30-fam'
        _Current_RB = {'name':'Current-RB','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        _Current_SP = {'name':'Current-SP','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_sextupole_s15_fam(_Base):
        """SI sextupole S15 power supply for horizontal correctors"""

        name = 'si-sextupole-s15-ch'
        _Current_RB = {'name':'Current-RB','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        _Current_SP = {'name':'Current-SP','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_sextupole_s15_ch(_Base):
        """SI sextupole S15 power supply for horizontal correctors"""

        name = 'si-sextupole-s15-ch'
        _Current_RB = {'name':'Current-RB','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        _Current_SP = {'name':'Current-SP','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class bo_quadrupole_qd_fam(_Base):
        """BO quadrupole QD power supply"""

        name = 'bo-quadrupole-qd-fam'
        _Current_RB = {'name':'Current-RB','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        _Current_SP = {'name':'Current-SP','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class bo_quadrupole_qf_fam(_Base):
        """BO quadrupole QF power supply"""

        name = 'bo-quadrupole-qf-fam'
        _Current_RB = {'name':'Current-RB','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        _Current_SP = {'name':'Current-SP','type':'float', 'value':0.0, 'prec':4, 'unit':'A',
                            'lolo'  :_sp_limits(name, 'LOLO'),
                            'lo'    :_sp_limits(name, 'LOW'),
                            'lolim' :_sp_limits(name, 'LOPR'),
                            'hilim' :_sp_limits(name, 'HOPR'),
                            'hi'    :_sp_limits(name, 'HIGH'),
                            'hihi'  :_sp_limits(name, 'HIHI')}
        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    @staticmethod
    def get_database(csdevice_type):
        csdevice_type = csdevice_type.replace('-','_')
        if csdevice_type in dir(__class__):
            return eval('PSClasses.' + csdevice_type +'.get_database()')

    @staticmethod
    def get_types():
        classes = []
        for method in dir(__class__):
            if method == '_Base': continue
            attr = getattr(__class__,method)
            if not isinstance(attr,type): continue
            if issubclass(getattr(__class__,method), PSClasses._Base):
                classes.append(method.replace('_','-'))
        return classes if classes else None





#
# from siriuspy.csdevice.enumtypes import EnumTypes as _et
# from siriuspy.csdevice.pvdb import PVDB as _PVDB
# from siriuspy.pwrsupply.psdata import get_setpoint_limits as _sp_limits
#
#
# # PSData object with all PS properties
# #_psdata = _get_psdata()
#
# class PSClasses:
#     """Magnet Power Supply PV Database Classes
#
#     These classes define all PVs associated with each type of power supply.
#
#     get_database(pstype_name):
#         A static method that returns a pcaspy-style database dictionary with all
#         properties that apply to the power supply type.
#
#     get_classes():
#         A static method of enclosing class MagPSPVDbClasses that returns the
#         names of power supply types for which PVDV classes are defined. These
#         names can be used with 'get_database'.
#     """
#
#     def _getdatabase(cls):
#         """Auxilliary function for MagPSPVDB classes to return databases with
#         all its PVDB properties."""
#         if 'get_database' in dir(super(cls)):
#             database = super(cls).get_database()
#         else:
#             database = {}
#         for attr_name in dir(cls):
#             attr_value = getattr(cls, attr_name)
#             if type(attr_value) is _PVDB:
#                 database[attr_value.name] = attr_value._asdict()
#         return database
#
#     class _Base:
#         _Reset_Cmd    = _PVDB(name='Reset-Cmd',    type='int',   value=0)
#         _CtrlMode_Mon = _PVDB(name='CtrlMode-Mon', type='enum',  enums=_et.enums('RmtLocTyp'),   value=_et.idx('RmtLocTyp', 'Remote'))
#         #_PwrState_Sel = _PVDB(name='PwrState-Sel', type='enum',  enums=_et.enums('OffOnTyp'),    value=_et.idx('OffOnTyp','On'))
#         _PwrState_Sel = _PVDB(name='PwrState-Sel', type='enum',  enums=_et.enums('OffOnTyp'),    value=None)
#         _PwrState_Sts = _PVDB(name='PwrState-Sts', type='enum',  enums=_et.enums('OffOnTyp'),    value=_et.idx('OffOnTyp','On'))
#         _OpMode_Sel   = _PVDB(name='OpMode-Sel',   type='enum',  enums=_et.enums('PSOpModeTyp'), value=_et.idx('PSOpModeTyp','SlowRef'))
#         _OpMode_Sts   = _PVDB(name='OpMode-Sts',   type='enum',  enums=_et.enums('PSOpModeTyp'), value=_et.idx('PSOpModeTyp','SlowRef'))
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_quadrupole_q14_fam(_Base):
#         """SI quadrupole Q14 power supply"""
#
#         name = 'si-quadrupole-q14-fam'
#         _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
#         #_Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
#         _Current_SP = _PVDB(name  ='Current-SP', type='float', value=None, prec=4, unit='A',
#                             lolo  =_sp_limits(name, 'LOLO'),
#                             lo    =_sp_limits(name, 'LOW'),
#                             lolim =_sp_limits(name, 'LOPR'),
#                             hilim =_sp_limits(name, 'HOPR'),
#                             hi    =_sp_limits(name, 'HIGH'),
#                             hihi  =_sp_limits(name, 'HIHI'),
#                            )
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_quadrupole_q20_fam(_Base):
#         """SI quadrupole Q20 power supply"""
#
#         name = 'si-quadrupole-q20-fam'
#         _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
#         _Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
#                             lolo  =_sp_limits(name, 'LOLO'),
#                             lo    =_sp_limits(name, 'LOW'),
#                             lolim =_sp_limits(name, 'LOPR'),
#                             hilim =_sp_limits(name, 'HOPR'),
#                             hi    =_sp_limits(name, 'HIGH'),
#                             hihi  =_sp_limits(name, 'HIHI'),
#                            )
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_quadrupole_q30_fam(_Base):
#         """SI quadrupole Q30 power supply"""
#
#         name = 'si-quadrupole-q30-fam'
#         _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
#         _Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
#                             lolo  =_sp_limits(name, 'LOLO'),
#                             lo    =_sp_limits(name, 'LOW'),
#                             lolim =_sp_limits(name, 'LOPR'),
#                             hilim =_sp_limits(name, 'HOPR'),
#                             hi    =_sp_limits(name, 'HIGH'),
#                             hihi  =_sp_limits(name, 'HIHI'),
#                            )
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_sextupole_s15_fam(_Base):
#         """SI sextupole S15 power supply for horizontal correctors"""
#
#         name = 'si-sextupole-s15-ch'
#         _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
#         _Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
#                             lolo  =_sp_limits(name, 'LOLO'),
#                             lo    =_sp_limits(name, 'LOW'),
#                             lolim =_sp_limits(name, 'LOPR'),
#                             hilim =_sp_limits(name, 'HOPR'),
#                             hi    =_sp_limits(name, 'HIGH'),
#                             hihi  =_sp_limits(name, 'HIHI'),
#                            )
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_sextupole_s15_ch(_Base):
#         """SI sextupole S15 power supply for horizontal correctors"""
#
#         name = 'si-sextupole-s15-ch'
#         _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
#         _Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
#                             lolo  =_sp_limits(name, 'LOLO'),
#                             lo    =_sp_limits(name, 'LOW'),
#                             lolim =_sp_limits(name, 'LOPR'),
#                             hilim =_sp_limits(name, 'HOPR'),
#                             hi    =_sp_limits(name, 'HIGH'),
#                             hihi  =_sp_limits(name, 'HIHI'),
#                            )
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_quadrupole_qd_fam(_Base):
#         """BO quadrupole QD power supply"""
#
#         name = 'bo-quadrupole-qd-fam'
#         _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
#         _Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
#                             lolo  =_sp_limits(name, 'LOLO'),
#                             lo    =_sp_limits(name, 'LOW'),
#                             lolim =_sp_limits(name, 'LOPR'),
#                             hilim =_sp_limits(name, 'HOPR'),
#                             hi    =_sp_limits(name, 'HIGH'),
#                             hihi  =_sp_limits(name, 'HIHI'),
#                            )
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_quadrupole_qf_fam(_Base):
#         """BO quadrupole QF power supply"""
#
#         name = 'bo-quadrupole-qf-fam'
#         _Current_RB = _PVDB(name  ='Current-RB', type='float', value=0.0, prec=4, unit='A')
#         _Current_SP = _PVDB(name  ='Current-SP', type='float', value=0.0, prec=4, unit='A',
#                             lolo  =_sp_limits(name, 'LOLO'),
#                             lo    =_sp_limits(name, 'LOW'),
#                             lolim =_sp_limits(name, 'LOPR'),
#                             hilim =_sp_limits(name, 'HOPR'),
#                             hi    =_sp_limits(name, 'HIGH'),
#                             hihi  =_sp_limits(name, 'HIHI'),
#                            )
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     @staticmethod
#     def get_database(csdevice_type):
#         csdevice_type = csdevice_type.replace('-','_')
#         if csdevice_type in dir(__class__):
#             return eval('PSClasses.' + csdevice_type +'.get_database()')
#
#     @staticmethod
#     def get_types():
#         classes = []
#         for method in dir(__class__):
#             if method == '_Base': continue
#             attr = getattr(__class__,method)
#             if not isinstance(attr,type): continue
#             if issubclass(getattr(__class__,method), PSClasses._Base):
#                 classes.append(method.replace('_','-'))
#         return classes if classes else None
