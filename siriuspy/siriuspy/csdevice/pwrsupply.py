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

default_intlklabels = ('Timeout',
                        'Bit1',
                        'Bit2',
                        'Bit3',
                        'Bit4',
                        'Bit5',
                        'Bit6',
                        'Bit7')



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

        _Reset_Cmd          = {'name':'Reset-Cmd',       'type':'int',    'value':0}
        _CtrlMode_Mon       = {'name':'CtrlMode-Mon',    'type':'enum',   'enums':_et.enums('RmtLocTyp'),   'value':_et.idx.Remote}
        _PwrState_Sel       = {'name':'PwrState-Sel',    'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.Off}
        _PwrState_Sts       = {'name':'PwrState-Sts',    'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.Off}
        _OpMode_Sel         = {'name':'OpMode-Sel',      'type':'enum',   'enums':_et.enums('PSOpModeTyp'), 'value':_et.idx.SlowRef}
        _OpMode_Sts         = {'name':'OpMode-Sts',      'type':'enum',   'enums':_et.enums('PSOpModeTyp'), 'value':_et.idx.SlowRef}
        _WfmIndex_Mon       = {'name':'WfmIndex-Mon',    'type':'int',    'value':0}
        _WfmLabels_Mon      = {'name':'WfmLabels-Mon',   'type':'string', 'count':len(default_wfmlabels), 'value':default_wfmlabels}
        _WfmLabel_SP        = {'name':'WfmLabel-SP',     'type':'string', 'count':1, 'value':default_wfmlabels[0]}
        _WfmLabel_RB        = {'name':'WfmLabel-RB',     'type':'string', 'count':1, 'value':default_wfmlabels[0]}
        _WfmLoad_Sel        = {'name':'WfmLoad-Sel',     'type':'enum',   'enums':default_wfmlabels,    'value':0}
        _WfmLoad_Sts        = {'name':'WfmLoad-Sts',     'type':'enum',   'enums':default_wfmlabels,    'value':0}
        _WfmData_SP         = {'name':'WfmData-SP',      'type':'float',  'count':default_wfmsize, 'value':[0.0 for datum in range(default_wfmsize)], 'unit':'A'}
        _WfmData_RB         = {'name':'WfmData-RB',      'type':'float',  'count':default_wfmsize, 'value':[0.0 for datum in range(default_wfmsize)], 'unit':'A'}
        _WfmSave_Cmd        = {'name':'WfmSave-Cmd',     'type':'int',    'value':0}
        _WfmScanning_Mon    = {'name':'WfmScanning-Mon', 'type':'int',    'value':0}
        _Intlk_Mon          = {'name':'Intlk-Mon',       'type':'int',    'value':0}
        _IntlkLabels_Cte    = {'name':'IntlkLabels-Cte', 'type':'string', 'count':8, 'value':default_intlklabels}


        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class _BaseLinac:

        _Reset_Cmd      = {'name':'Reset-Cmd',      'type':'int',    'value':0}
        _CtrlMode_Mon   = {'name':'CtrlMode-Mon',   'type':'enum',   'enums':_et.enums('RmtLocTyp'),   'value':_et.idx.Remote}
        _PwrState_Sel   = {'name':'PwrState-Sel',   'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.On}
        _PwrState_Sts   = {'name':'PwrState-Sts',   'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.On}

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
        del(_db)

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
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_quadrupole_qs(_Base):
        """SI skew quadrupole magnet power supply"""

        name = 'si-quadrupole-qs'
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
        del(_db)

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
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class si_sextupole_s15_cv(_Base):
        """SI sextupole S15 power supply for vertical correctors"""

        name = 'si-sextupole-s15-cv'
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

    class si_sextupole_s15_qs(_Base):
        """SI sextupole S15 power supply for skew quadrupoles"""

        name = 'si-sextupole-s15-qs'
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

    class si_corrector_cv(_Base):
        """SI vertical corrector power supply"""

        name = 'si-corrector-cv'
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

    class si_corrector_fch(_Base):
        """SI fast horizontal corrector power supply"""

        name = 'si-corrector-fch'
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

    class si_corrector_fcv(_Base):
        """SI fast vertical corrector power supply"""

        name = 'si-corrector-fcv'
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

    class si_injdpk(_Base):
        """SI injection dipolar kicker power supply"""

        name = 'si-injdpk'
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

    class si_injnlk(_Base):
        """SI injection non-linear kicker power supply"""

        name = 'si-injnlk'
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

    class si_hping(_Base):
        """SI horizontal pinger power supply"""

        name = 'si-hping'
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

    class si_vping(_Base):
        """SI vertical pinger power supply"""

        name = 'si-vping'
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

    class ts_dipole_b_fam(_Base):
        """TS dipole B power supply"""

        name = 'ts-dipole-b-fam'
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

    class ts_quadrupole_q14(_Base):
        """TS quadrupole Q14 power supply"""

        name = 'ts-quadrupole-q14'
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

    class ts_quadrupole_q20(_Base):
        """TS quadrupole Q20 power supply"""

        name = 'ts-quadrupole-q20'
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

    class ts_corrector_ch(_Base):
        """TS horizontal corrector power supply"""

        name = 'ts-corrector-ch'
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

    class ts_corrector_cv(_Base):
        """TS vertical corrector power supply"""

        name = 'ts-corrector-cv'
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

    class ts_injseptum_thick(_Base):
        """TS thick injection septum power supply"""

        name = 'ts-injseptum-thick'
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

    class ts_injseptum_thin(_Base):
        """TS thin injection septum power supply"""

        name = 'ts-injseptum-thin'
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

    class ts_ejeseptum_thick(_Base):
        """TS thick ejection septum power supply"""

        name = 'ts-ejeseptum-thick'
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

    class ts_ejeseptum_thin(_Base):
        """TS thin ejection septum power supply"""

        name = 'ts-ejeseptum-thin'
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

    class bo_dipole_b_fam(_Base):
        """BO dipole B power supply"""

        name = 'bo-dipole-b-fam'
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
        del(_db)

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
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    class bo_quadrupole_qs(_Base):
        """BO quadrupole QS power supply"""

        name = 'bo-quadrupole-qs'
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

    class bo_sextupole_sd_fam(_Base):
        """BO sextupole SD power supply"""

        name = 'bo-sextupole-sd-fam'
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

    class bo_sextupole_sf_fam(_Base):
        """BO sextupole SF power supply"""

        name = 'bo-sextupole-sf-fam'
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

    class bo_corrector_ch(_Base):
        """BO horizontal corrector power supply"""

        name = 'bo-corrector-ch'
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

    class bo_corrector_cv(_Base):
        """BO vertical corrector power supply"""

        name = 'bo-corrector-cv'
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

    class bo_injkicker(_Base):
        """BO injection kicker power supply"""

        name = 'bo-injkicker'
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

    class bo_ejekicker(_Base):
        """BO ejection kicker power supply"""

        name = 'bo-ejekicker'
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

    class tb_dipole_b_fam(_Base):
        """TB dipole B power supply"""

        name = 'tb-dipole-b-fam'
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

    class tb_quadrupole(_Base):
        """TB quadrupole power supply"""

        name = 'tb-quadrupole'
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

    class tb_corrector_ch(_Base):
        """TB horizontal corrector power supply"""

        name = 'tb-corrector-ch'
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

    class tb_corrector_cv(_Base):
        """TB vertical corrector power supply"""

        name = 'tb-corrector-cv'
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

    class tb_injseptum(_Base):
        """TB injection septum power supply"""

        name = 'tb-injseptum'
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

    #class li_spect(_BaseLinac):
    class li_spect(_Base):
        """LI spectrometer power supply"""

        name = 'li-spect'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    #class li_solenoid_fam(_BaseLinac):
    class li_solenoid_fam(_Base):
        """LI solenoid family power supply"""

        name = 'li-solenoid-fam'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    #class li_solenoid(_BaseLinac):
    class li_solenoid(_Base):
        """LI individual solenoid power supply"""

        name = 'li-solenoid'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    #class li_quadrupole_long(_BaseLinac):
    class li_quadrupole_long(_Base):
        """LI long quadrupole power supply"""

        name = 'li-quadrupole-long'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    #class li_quadrupole_short(_BaseLinac):
    class li_quadrupole_short(_Base):
        """LI short quadrupole power supply"""

        name = 'li-quadrupole-short'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    #class li_corrector_ch_long(_BaseLinac):
    class li_corrector_ch_long(_Base):
        """LI long horizontal corrector power supply"""

        name = 'li-corrector-ch-long'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    #class li_corrector_cv_long(_BaseLinac):
    class li_corrector_cv_long(_Base):
        """LI long vertical corrector power supply"""

        name = 'li-corrector-cv-long'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    #class li_corrector_ch_short(_BaseLinac):
    class li_corrector_ch_short(_Base):
        """LI short horizontal corrector power supply"""

        name = 'li-corrector-ch-short'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    #class li_corrector_cv_short(_BaseLinac):
    class li_corrector_cv_short(_Base):
        """LI short vertical corrector power supply"""

        name = 'li-corrector-cv-short'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

        @staticmethod
        def get_database(): return PSClasses._getdatabase(__class__)

    #class li_lens(_BaseLinac):
    class li_lens(_Base):
        """LI lens power supply"""

        name = 'li-lens'
        _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
               'lolo'  :_ps_sp_lims(name, 'LOLO'),
               'lo'    :_ps_sp_lims(name, 'LOW'),
               'lolim' :_ps_sp_lims(name, 'LOPR'),
               'hilim' :_ps_sp_lims(name, 'HOPR'),
               'hi'    :_ps_sp_lims(name, 'HIGH'),
               'hihi'  :_ps_sp_lims(name, 'HIHI')}
        _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
        _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
        del(_db)

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
            if method in ('_Base','_BaseLinac'): continue
            attr = getattr(__class__,method)
            if not isinstance(attr,type): continue
            if issubclass(getattr(__class__,method), PSClasses._Base):
                classes.append(method.replace('_','-'))
        return classes if classes else None
