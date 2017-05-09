import copy as _copy
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.pwrsupply.psdata import get_setpoint_limits as _ps_sp_lims
#from siriuspy.pwrsupply.controller import ControllerSim as _ControllerSim


default_wfmsize   = 2000
default_wfmlabels = ('Waveform1', # These are the waveform slot labels
                     'Waveform2', # with which waveforms stored in
                     'Waveform3', # non-volatile memory may be selected
                     'Waveform4', # with the WfmLoad-Sel PV.
                     'Waveform5',
                     'Waveform6')


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

        _Reset_Cmd      = {'name':'Reset-Cmd',      'type':'int',    'value':0}
        _CtrlMode_Mon   = {'name':'CtrlMode-Mon',   'type':'enum',   'enums':_et.enums('RmtLocTyp'),   'value':_et.idx.Remote}
        _PwrState_Sel   = {'name':'PwrState-Sel',   'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.On}
        _PwrState_Sts   = {'name':'PwrState-Sts',   'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.On}
        _OpMode_Sel     = {'name':'OpMode-Sel',     'type':'enum',   'enums':_et.enums('PSOpModeTyp'), 'value':_et.idx.SlowRef}
        _OpMode_Sts     = {'name':'OpMode-Sts',     'type':'enum',   'enums':_et.enums('PSOpModeTyp'), 'value':_et.idx.SlowRef}
        _WfmIndex_Mon   = {'name':'WfmIndex-Mon',   'type':'int',    'value':0}
        _WfmLabels_Mon  = {'name':'WfmLabels-Mon',  'type':'string', 'count':len(default_wfmlabels), 'value':default_wfmlabels}
        _WfmLabel_SP    = {'name':'WfmLabel-SP',    'type':'string', 'count':1, 'value':default_wfmlabels[0]}
        _WfmLabel_RB    = {'name':'WfmLabel-RB',    'type':'string', 'count':1, 'value':default_wfmlabels[0]}
        _WfmLoad_Sel    = {'name':'WfmLoad-Sel',    'type':'enum',   'enums':default_wfmlabels,    'value':0}
        _WfmLoad_Sts    = {'name':'WfmLoad-Sts',    'type':'enum',   'enums':default_wfmlabels,    'value':0}
        _WfmData_SP     = {'name':'WfmData-SP',     'type':'float',  'count':default_wfmsize, 'value':[datum for datum in range(default_wfmsize)], 'unit':'A'}
        _WfmData_RB     = {'name':'WfmData-RB',     'type':'float',  'count':default_wfmsize, 'value':[datum for datum in range(default_wfmsize)], 'unit':'A'}
        _WfmSave_Cmd    = {'name':'WfmSave-Cmd',    'type':'int',    'value':0}

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_dipole_b1b2_fam(_Base):
        """SI dipole B1B2 power supply"""

        name = 'si-dipole-b1b2-fam'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_quadrupole_q14_fam(_Base):
        """SI quadrupole Q14 power supply"""

        name = 'si-quadrupole-q14-fam'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_quadrupole_q20_fam(_Base):
        """SI quadrupole Q20 power supply"""

        name = 'si-quadrupole-q20-fam'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_quadrupole_q30_fam(_Base):
        """SI quadrupole Q30 power supply"""

        name = 'si-quadrupole-q30-fam'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_quadrupole_q14_trim(_Base):
        """SI quadrupole Q14 trim power supply"""

        name = 'si-quadrupole-q14-trim'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_quadrupole_q20_trim(_Base):
        """SI quadrupole Q20 trim power supply"""

        name = 'si-quadrupole-q20-trim'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_quadrupole_q30_trim(_Base):
        """SI quadrupole Q30 trim power supply"""

        name = 'si-quadrupole-q30-trim'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_sextupole_s15_fam(_Base):
        """SI sextupole S15 power supply for horizontal correctors"""

        name = 'si-sextupole-s15-ch'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_sextupole_s15_ch(_Base):
        """SI sextupole S15 power supply for horizontal correctors"""

        name = 'si-sextupole-s15-ch'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class bo_quadrupole_qd_fam(_Base):
        """BO quadrupole QD power supply"""

        name = 'bo-quadrupole-qd-fam'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class bo_quadrupole_qf_fam(_Base):
        """BO quadrupole QF power supply"""

        name = 'bo-quadrupole-qf-fam'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
        _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})

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
