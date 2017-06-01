import copy as _copy
import siriuspy.servweb as _web
import siriuspy.util as _util
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.search import PSSearch as _PSSearch

#from siriuspy.pwrsupply import psdata as _psdata

default_wfmsize   = 2000
default_wfmlabels =_et.enums('PSWfmLabelsTyp')
default_intlklabels = _et.enums('PSIntlkLabelsTyp')

#_util.conv_splims_labels(label)

def create_commun_propty_database():
    db = {
        'CtrlMode-Mon'       : {'type':'enum',   'enums':_et.enums('RmtLocTyp'),   'value':_et.idx.Remote},
        'PwrState-Sel'       : {'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.Off},
        'PwrState-Sts'       : {'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.Off},
        'OpMode-Sel'         : {'type':'enum',   'enums':_et.enums('PSOpModeTyp'), 'value':_et.idx.SlowRef},
        'OpMode-Sts'         : {'type':'enum',   'enums':_et.enums('PSOpModeTyp'), 'value':_et.idx.SlowRef},
        'Reset-Cmd'          : {'type':'int',    'value':0},
        'Abort-Cmd'          : {'type':'int',    'value':0},
        'WfmIndex-Mon'       : {'type':'int',    'value':0},
        'WfmLabels-Mon'      : {'type':'string', 'count':len(default_wfmlabels), 'value':default_wfmlabels},
        'WfmLabel-SP'        : {'type':'string', 'value':default_wfmlabels[0]},
        'WfmLabel-RB'        : {'type':'string', 'value':default_wfmlabels[0]},
        'WfmLoad-Sel'        : {'type':'enum',   'enums':default_wfmlabels,    'value':0},
        'WfmLoad-Sts'        : {'type':'enum',   'enums':default_wfmlabels,    'value':0},
        'WfmData-SP'         : {'type':'float',  'count':default_wfmsize, 'value':[0.0 for datum in range(default_wfmsize)], 'unit':'A'},
        'WfmData-RB'         : {'type':'float',  'count':default_wfmsize, 'value':[0.0 for datum in range(default_wfmsize)], 'unit':'A'},
        'WfmSave-Cmd'        : {'type':'int',    'value':0},
        'Intlk-Mon'          : {'type':'int',    'value':0},
        'IntlkLabels-Cte'    : {'type':'string', 'count':8, 'value':default_intlklabels},
        'Current-SP'         : {'type':'float',  'value':0.0, 'prec':4},
        'Current-RB'         : {'type':'float',  'value':0.0, 'prec':4},
        'CurrentRef-Mon'     : {'type':'float',  'value':0.0, 'prec':4},
        'Current-Mon'        : {'type':'float',  'value':0.0, 'prec':4},
    }
    return db

def get_propty_database(pstype):
    """Returns property database of a power supply type device."""
    propty_db = create_commun_propty_database()
    splims = _PSSearch.conv_pstype_2_splims(pstype)
    units = _PSSearch.get_splims_unit()
    for propty,db in propty_db.items():
        # set setpoint limits in database
        if propty in ('Current-SP',):
            label='lolo';  db[label] = _PSSearch.get_splim(pstype,label)
            label='low';   db[label] = _PSSearch.get_splim(pstype,label)
            label='lolim'; db[label] = _PSSearch.get_splim(pstype,label)
            label='hilim'; db[label] = _PSSearch.get_splim(pstype,label)
            label='high';  db[label] = _PSSearch.get_splim(pstype,label)
            label='hihi';  db[label] = _PSSearch.get_splim(pstype,label)
        # define unit of current
        if propty in ('Current-SP','Current-RB','CurrentRef-Mon','Current-Mon'):
            db['unit'] = units[0]

    return propty_db


# _timeout = None
#
# class PSSetPointLims:
#
#     def __init__(self, timeout=_timeout):
#
#         self._ps_name_list = None
#         self._pstype_name_list = None
#         self._pstype2ps_dict = None
#         self._ps2pstype_dict = None
#         self._setpoint_unit = None
#         self._pstype_polarity_list = None
#         self._pstype_sp_limits_dict = None
#         self._setpoint_limit_labels = None
#
#         if _web.server_online():
#             pstypes_text = _web.power_supplies_pstypes_names_read(timeout=timeout)
#             self._build_pstype_data(pstypes_text)
#             self._build_ps_data()
#             self._build_pstype_sp_limits()
#
#     def _build_ps_data(self):
#
#         # read data from files in the web server and build pstype2ps dict
#         self._pstype2ps_dict = {}
#         for name in self._pstype_name_list:
#             text = _web.power_supplies_pstype_data_read(name + '.txt', timeout=_timeout)
#             psnames, param_dict = self._read_text_pstype(text)
#             self._pstype2ps_dict[name] = tuple(psnames)
#
#         # build ps2pstype dict
#         self._ps2pstype_dict = {}
#         for pstype_name in self._pstype_name_list:
#             for ps_name in self._pstype2ps_dict[pstype_name]:
#                 if ps_name in self._ps2pstype_dict:
#                     raise Exception('power supply "' + ps_name + '" is listed in more than one power supply type files!')
#                 else:
#                     self._ps2pstype_dict[ps_name] = pstype_name
#
#         self._ps_name_list = sorted([_PVName(key) for key in self._ps2pstype_dict.keys()])
#
#     def _build_pstype_data(self, text):
#         data, _ = _util.read_text_data(text)
#         names, polarities = [], []
#         for datum in data:
#             name, polarity = datum[0], datum[1]
#             names.append(name), polarities.append(polarity)
#         self._pstype_name_list = tuple(names)
#         self._pstype_polarity_list = tuple(polarities)
#
#     def _build_pstype_sp_limits(self):
#         text = _web.power_supplies_pstype_setpoint_limits(timeout=_timeout)
#         data, param_dict = _util.read_text_data(text)
#         self._setpoint_unit = tuple(param_dict['unit'])
#         self._setpoint_limit_labels = tuple(param_dict['power_supply_type'])
#         self._pstype_sp_limits_dict = {pstype_name:[None,]*len(data[0]) for pstype_name in self._pstype_name_list}
#         for line in data:
#             pstype_name, *limits = line
#             self._pstype_sp_limits_dict[pstype_name] = [float(limit) for limit in limits]
#         for pstype_name in self._pstype_name_list:
#             self._pstype_sp_limits_dict[pstype_name] = tuple(self._pstype_sp_limits_dict[pstype_name])
#
#     def _read_text_pstype(self, text):
#         data, param_dict = _util.read_text_data(text)
#         psnames = []
#         for datum in data:
#             psnames.append(datum[0])
#         return psnames, param_dict
#
#     def get_setpoint_limits(self, psname, *limit_labels):
#         """Return setpoint limits of given power supply of power suppy type.
#
#         Arguments:
#
#         psname -- name of power supply of power supply type
#         limit_labels -- limit labels of interest
#                        a) it can be a sequence of strings, each for a limit name of interest
#                        b) if not passed, all defined limits are returned
#                        c) if a single string, the single value of the the corresponding limit is returned
#
#         returns:
#
#         A dictionary with name and value pair of the requested limits.
#         In case of a string argument for single limit name, a single value is
#         returned.
#         """
#
#         if self._pstype_name_list is None: return None
#
#         if psname in self._pstype_name_list:
#             values = self._pstype_sp_limits_dict[psname]
#         elif psname in self._ps_name_list:
#             pstype_name  = self._ps2pstype_dict[psname]
#             values = self._pstype_sp_limits_dict[pstype_name]
#         else:
#             return None
#
#         if len(limit_labels) == 0:
#             limit_labels = self._setpoint_limit_labels
#         if len(limit_labels) == 1 and isinstance(limit_labels[0], str):
#             idx = self._setpoint_limit_labels.index(limit_labels[0])
#             return values[idx]
#
#         limits_dict = {}
#         for limit_name in limit_labels:
#             idx = self._setpoint_limit_labels.index(limit_name)
#             limits_dict[limit_name] = values[idx]
#         return limits_dict
#
# # this code needs optimization in order to make import lighter!
# # see what has been donw for MAClass...
# _pslims = PSSetPointLims()
# _ps_sp_lims = _pslims.get_setpoint_limits
# def get_pssplims():
#     global _pslims
#     if _pslims is None:
#         _pslims = PSSetPointLims(timeout=_timeout)
#     return _pslims
#
#
# class MASetPointLims:
#
#     def __init__(self, timeout=_timeout):
#
#         self.mag2ps_dict = None
#         self.ps2mag_dict = None
#         self.magps_sp_limits_dict = None
#
#         if _web.server_online():
#             self._build_mag_sp_limits(timeout)
#             self._build_mag_excitation_dict()
#
#     def _build_mag_sp_limits(self, timeout=_timeout):
#         text = _web.magnets_setpoint_limits(timeout=timeout)
#         data, param_dict = _util.read_text_data(text)
#         self.setpoint_unit = tuple(param_dict['unit'])
#         self._setpoint_limit_labels = tuple(param_dict['power_supply_type'])
#         self.magps_sp_limits_dict = {}
#         for line in data:
#             magps_name, *limits = line
#             db = {self._setpoint_limit_labels[i]:float(limits[i]) for i in range(len(self._setpoint_limit_labels))}
#             self.magps_sp_limits_dict[magps_name] = db
#
#     def _build_mag_excitation_dict(self, timeout=_timeout):
#         text = _web.magnets_excitation_ps_read(timeout=timeout)
#         data, param_dict = _util.read_text_data(text)
#         self.mag2ps_dict = {}
#         self.ps2mag_dict = {}
#         for datum in data:
#             magnet, *ps_names = datum
#             self.mag2ps_dict[magnet] = tuple(ps_names)
#             for ps_name in ps_names:
#                 try:
#                     self.ps2mag_dict[ps_name].append(magnet)
#                 except:
#                     self.ps2mag_dict[ps_name] = [magnet]
#
#     def conv_mag2ps(self, magname):
#         return tuple(self.mag2ps_dict[magname])
#
#     def conv_ps2mag(self, psname):
#         return tuple(self.ps2mag_dict[psname])
#
#     def get_setpoint_limits(self, maname, *limit_labels):
#
#         values = self.magps_sp_limits_dict[maname]
#
#         if len(limit_labels) == 0:
#             limit_labels = self._setpoint_limit_labels
#         if len(limit_labels) == 1 and isinstance(limit_labels[0], str):
#             idx = self._setpoint_limit_labels.index(limit_labels[0])
#             return values[idx]
#
#         limits_dict = {}
#         for limit_name in limit_labels:
#             #idx = self._setpoint_limit_labels.index(limit_name)
#             limits_dict[limit_name] = values[limit_name]
#         return limits_dict
#
# _malims = None
# def get_masplims():
#     global _malims
#     if _malims is None:
#         _malims = MASetPointLims(timeout=_timeout)
#     return _malims
#
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
#             if type(attr_value) is dict:
#                 d = _copy.deepcopy(attr_value)
#                 del d['name']
#                 database[attr_value['name']] = d
#         return database
#
#     class _Base:
#
#         _CtrlMode_Mon       = {'name':'CtrlMode-Mon',    'type':'enum',   'enums':_et.enums('RmtLocTyp'),   'value':_et.idx.Remote}
#         _PwrState_Sel       = {'name':'PwrState-Sel',    'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.Off}
#         _PwrState_Sts       = {'name':'PwrState-Sts',    'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.Off}
#         _OpMode_Sel         = {'name':'OpMode-Sel',      'type':'enum',   'enums':_et.enums('PSOpModeTyp'), 'value':_et.idx.SlowRef}
#         _OpMode_Sts         = {'name':'OpMode-Sts',      'type':'enum',   'enums':_et.enums('PSOpModeTyp'), 'value':_et.idx.SlowRef}
#         _Reset_Cmd          = {'name':'Reset-Cmd',       'type':'int',    'value':0}
#         _Abort_Cmd          = {'name':'Abort-Cmd',       'type':'int',    'value':0}
#         _WfmIndex_Mon       = {'name':'WfmIndex-Mon',    'type':'int',    'value':0}
#         _WfmLabel_SP        = {'name':'WfmLabel-SP',     'type':'string', 'count':1, 'value':default_wfmlabels[0]}
#         _WfmLabel_RB        = {'name':'WfmLabel-RB',     'type':'string', 'count':1, 'value':default_wfmlabels[0]}
#         _WfmLabels_Mon      = {'name':'WfmLabels-Mon',   'type':'string', 'count':len(default_wfmlabels), 'value':default_wfmlabels}
#         _WfmLoad_Sel        = {'name':'WfmLoad-Sel',     'type':'enum',   'enums':default_wfmlabels,    'value':0}
#         _WfmLoad_Sts        = {'name':'WfmLoad-Sts',     'type':'enum',   'enums':default_wfmlabels,    'value':0}
#         _WfmData_SP         = {'name':'WfmData-SP',      'type':'float',  'count':default_wfmsize, 'value':[0.0 for datum in range(default_wfmsize)], 'unit':'A'}
#         _WfmData_RB         = {'name':'WfmData-RB',      'type':'float',  'count':default_wfmsize, 'value':[0.0 for datum in range(default_wfmsize)], 'unit':'A'}
#         _WfmSave_Cmd        = {'name':'WfmSave-Cmd',     'type':'int',    'value':0}
#         _Intlk_Mon          = {'name':'Intlk-Mon',       'type':'int',    'value':0}
#         _IntlkLabels_Cte    = {'name':'IntlkLabels-Cte', 'type':'string', 'count':8, 'value':default_intlklabels}
#
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class _BaseLinac:
#
#         _Reset_Cmd      = {'name':'Reset-Cmd',      'type':'int',    'value':0}
#         _CtrlMode_Mon   = {'name':'CtrlMode-Mon',   'type':'enum',   'enums':_et.enums('RmtLocTyp'),   'value':_et.idx.Remote}
#         _PwrState_Sel   = {'name':'PwrState-Sel',   'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.On}
#         _PwrState_Sts   = {'name':'PwrState-Sts',   'type':'enum',   'enums':_et.enums('OffOnTyp'),    'value':_et.idx.On}
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_dipole_b1b2_fam(_Base):
#         """SI dipole B1B2 power supply"""
#
#         name = 'si-dipole-b1b2-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_quadrupole_q14_fam(_Base):
#         """SI quadrupole Q14 power supply"""
#
#         name = 'si-quadrupole-q14-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_quadrupole_q20_fam(_Base):
#         """SI quadrupole Q20 power supply"""
#
#         name = 'si-quadrupole-q20-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_quadrupole_q30_fam(_Base):
#         """SI quadrupole Q30 power supply"""
#
#         name = 'si-quadrupole-q30-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_quadrupole_q14_trim(_Base):
#         """SI quadrupole Q14 trim power supply"""
#
#         name = 'si-quadrupole-q14-trim'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_quadrupole_q20_trim(_Base):
#         """SI quadrupole Q20 trim power supply"""
#
#         name = 'si-quadrupole-q20-trim'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_quadrupole_q30_trim(_Base):
#         """SI quadrupole Q30 trim power supply"""
#
#         name = 'si-quadrupole-q30-trim'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_quadrupole_qs(_Base):
#         """SI skew quadrupole magnet power supply"""
#
#         name = 'si-quadrupole-qs'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_sextupole_s15_fam(_Base):
#         """SI sextupole S15 power supply for horizontal correctors"""
#
#         name = 'si-sextupole-s15-ch'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_sextupole_s15_ch(_Base):
#         """SI sextupole S15 power supply for horizontal correctors"""
#
#         name = 'si-sextupole-s15-ch'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_sextupole_s15_cv(_Base):
#         """SI sextupole S15 power supply for vertical correctors"""
#
#         name = 'si-sextupole-s15-cv'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_sextupole_s15_qs(_Base):
#         """SI sextupole S15 power supply for skew quadrupoles"""
#
#         name = 'si-sextupole-s15-qs'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_corrector_cv(_Base):
#         """SI vertical corrector power supply"""
#
#         name = 'si-corrector-cv'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_corrector_fch(_Base):
#         """SI fast horizontal corrector power supply"""
#
#         name = 'si-corrector-fch'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_corrector_fcv(_Base):
#         """SI fast vertical corrector power supply"""
#
#         name = 'si-corrector-fcv'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_injdpk(_Base):
#         """SI injection dipolar kicker power supply"""
#
#         name = 'si-injdpk'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_injnlk(_Base):
#         """SI injection non-linear kicker power supply"""
#
#         name = 'si-injnlk'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_hping(_Base):
#         """SI horizontal pinger power supply"""
#
#         name = 'si-hping'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class si_vping(_Base):
#         """SI vertical pinger power supply"""
#
#         name = 'si-vping'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class ts_dipole_b_fam(_Base):
#         """TS dipole B power supply"""
#
#         name = 'ts-dipole-b-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class ts_quadrupole_q14(_Base):
#         """TS quadrupole Q14 power supply"""
#
#         name = 'ts-quadrupole-q14'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class ts_quadrupole_q20(_Base):
#         """TS quadrupole Q20 power supply"""
#
#         name = 'ts-quadrupole-q20'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class ts_corrector_ch(_Base):
#         """TS horizontal corrector power supply"""
#
#         name = 'ts-corrector-ch'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class ts_corrector_cv(_Base):
#         """TS vertical corrector power supply"""
#
#         name = 'ts-corrector-cv'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class ts_injseptum_thick(_Base):
#         """TS thick injection septum power supply"""
#
#         name = 'ts-injseptum-thick'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class ts_injseptum_thin(_Base):
#         """TS thin injection septum power supply"""
#
#         name = 'ts-injseptum-thin'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class ts_ejeseptum_thick(_Base):
#         """TS thick ejection septum power supply"""
#
#         name = 'ts-ejeseptum-thick'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class ts_ejeseptum_thin(_Base):
#         """TS thin ejection septum power supply"""
#
#         name = 'ts-ejeseptum-thin'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_dipole_b_fam(_Base):
#         """BO dipole B power supply"""
#
#         name = 'bo-dipole-b-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_quadrupole_qd_fam(_Base):
#         """BO quadrupole QD power supply"""
#
#         name = 'bo-quadrupole-qd-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_quadrupole_qf_fam(_Base):
#         """BO quadrupole QF power supply"""
#
#         name = 'bo-quadrupole-qf-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_quadrupole_qs(_Base):
#         """BO quadrupole QS power supply"""
#
#         name = 'bo-quadrupole-qs'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_sextupole_sd_fam(_Base):
#         """BO sextupole SD power supply"""
#
#         name = 'bo-sextupole-sd-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_sextupole_sf_fam(_Base):
#         """BO sextupole SF power supply"""
#
#         name = 'bo-sextupole-sf-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_corrector_ch(_Base):
#         """BO horizontal corrector power supply"""
#
#         name = 'bo-corrector-ch'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_corrector_cv(_Base):
#         """BO vertical corrector power supply"""
#
#         name = 'bo-corrector-cv'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_injkicker(_Base):
#         """BO injection kicker power supply"""
#
#         name = 'bo-injkicker'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class bo_ejekicker(_Base):
#         """BO ejection kicker power supply"""
#
#         name = 'bo-ejekicker'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class tb_dipole_b_fam(_Base):
#         """TB dipole B power supply"""
#
#         name = 'tb-dipole-b-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class tb_quadrupole(_Base):
#         """TB quadrupole power supply"""
#
#         name = 'tb-quadrupole'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class tb_corrector_ch(_Base):
#         """TB horizontal corrector power supply"""
#
#         name = 'tb-corrector-ch'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class tb_corrector_cv(_Base):
#         """TB vertical corrector power supply"""
#
#         name = 'tb-corrector-cv'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     class tb_injseptum(_Base):
#         """TB injection septum power supply"""
#
#         name = 'tb-injseptum'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_RB     = _copy.deepcopy(_db); _Current_RB.update({'name':'Current-RB'})
#         _CurrentRef_Mon = _copy.deepcopy(_db); _CurrentRef_Mon.update({'name':'CurrentRef-Mon'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     #class li_spect(_BaseLinac):
#     class li_spect(_Base):
#         """LI spectrometer power supply"""
#
#         name = 'li-spect'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     #class li_solenoid_fam(_BaseLinac):
#     class li_solenoid_fam(_Base):
#         """LI solenoid family power supply"""
#
#         name = 'li-solenoid-fam'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     #class li_solenoid(_BaseLinac):
#     class li_solenoid(_Base):
#         """LI individual solenoid power supply"""
#
#         name = 'li-solenoid'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     #class li_quadrupole_long(_BaseLinac):
#     class li_quadrupole_long(_Base):
#         """LI long quadrupole power supply"""
#
#         name = 'li-quadrupole-long'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     #class li_quadrupole_short(_BaseLinac):
#     class li_quadrupole_short(_Base):
#         """LI short quadrupole power supply"""
#
#         name = 'li-quadrupole-short'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     #class li_corrector_ch_long(_BaseLinac):
#     class li_corrector_ch_long(_Base):
#         """LI long horizontal corrector power supply"""
#
#         name = 'li-corrector-ch-long'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     #class li_corrector_cv_long(_BaseLinac):
#     class li_corrector_cv_long(_Base):
#         """LI long vertical corrector power supply"""
#
#         name = 'li-corrector-cv-long'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     #class li_corrector_ch_short(_BaseLinac):
#     class li_corrector_ch_short(_Base):
#         """LI short horizontal corrector power supply"""
#
#         name = 'li-corrector-ch-short'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     #class li_corrector_cv_short(_BaseLinac):
#     class li_corrector_cv_short(_Base):
#         """LI short vertical corrector power supply"""
#
#         name = 'li-corrector-cv-short'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
#         @staticmethod
#         def get_database(): return PSClasses._getdatabase(__class__)
#
#     #class li_lens(_BaseLinac):
#     class li_lens(_Base):
#         """LI lens power supply"""
#
#         name = 'li-lens'
#         _db = {'type':'float', 'value':0.0, 'prec':4, 'unit':'A',
#                'lolo'  :_ps_sp_lims(name, 'LOLO'),
#                'low'   :_ps_sp_lims(name, 'LOW'),
#                'lolim' :_ps_sp_lims(name, 'LOPR'),
#                'hilim' :_ps_sp_lims(name, 'HOPR'),
#                'high'  :_ps_sp_lims(name, 'HIGH'),
#                'hihi'  :_ps_sp_lims(name, 'HIHI')}
#         _Current_SP     = _copy.deepcopy(_db); _Current_SP.update({'name':'Current-SP'})
#         _Current_Mon    = _copy.deepcopy(_db); _Current_Mon.update({'name':'Current-Mon'})
#         del(_db)
#
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
#             if method in ('_Base','_BaseLinac'): continue
#             attr = getattr(__class__,method)
#             if not isinstance(attr,type): continue
#             if issubclass(getattr(__class__,method), PSClasses._Base):
#                 classes.append(method.replace('_','-'))
#         return classes if classes else None
#
#
# class MAClass:
#
#     @staticmethod
#     def get_database(maname):
#         masplims = get_masplims()
#         pssplims = get_pssplims()
#         psnames = masplims.conv_mag2ps(maname)
#         db = {}
#         for psname in psnames:
#             #print(psname)
#             pstype = pssplims._ps2pstype_dict[psname]
#             maname_ps = psname.replace(':PS-',':MA-')
#             db[maname_ps] = PSClasses.get_database(pstype)
#             lims = masplims.get_setpoint_limits(maname_ps)
#             sp_lims = {}
#             sp_lims['lolo']  = lims['LOLO']
#             sp_lims['low']   = lims['LOW']
#             sp_lims['lolim'] = lims['LOPR']
#             sp_lims['hilim'] = lims['HOPR']
#             sp_lims['high']  = lims['HIGH']
#             sp_lims['hihi']  = lims['HIHI']
#             if 'Current-SP' in db[maname_ps]: db[maname_ps]['Current-SP'].update(sp_lims)
#             if 'Current-RB' in db[maname_ps]: db[maname_ps]['Current-RB'].update(sp_lims)
#             if 'CurrentRef-Mon' in db[maname_ps]: db[maname_ps]['CurrentRef-Mon'].update(sp_lims)
#             if 'Current-Mon' in db[maname_ps]: db[maname_ps]['Current-Mon'].update(sp_lims)
#             # func = pssplims._pstype2func_dict[pstype]
#             # if func in ('quadrupole', 'quadrupole-skew'):
#             #     db[maname_ps]['KL-SP']     = {'type':'float', 'value':0.0, 'prec':6, 'unit':'1/m'}
#             #     db[maname_ps]['KL-RB']     = {'type':'float', 'value':0.0, 'prec':6, 'unit':'1/m'}
#             #     db[maname_ps]['KLRef-Mon'] = {'type':'float', 'value':0.0, 'prec':6, 'unit':'1/m'}
#             #     db[maname_ps]['KL-Mon']    = {'type':'float', 'value':0.0, 'prec':6, 'unit':'1/m'}
#             # elif func == 'sextupole':
#             #     db[maname_ps]['SL-SP']     = {'type':'float', 'value':0.0, 'prec':6, 'unit':'1/m^2'}
#             #     db[maname_ps]['SL-RB']     = {'type':'float', 'value':0.0, 'prec':6, 'unit':'1/m^2'}
#             #     db[maname_ps]['SLRef-Mon'] = {'type':'float', 'value':0.0, 'prec':6, 'unit':'1/m^2'}
#             #     db[maname_ps]['SL-Mon']    = {'type':'float', 'value':0.0, 'prec':6, 'unit':'1/m^2'}
#             # elif func == 'corrector':
#             #     db[maname_ps]['Kick-SP']     = {'type':'float', 'value':0.0, 'prec':8, 'unit':'rad'}
#             #     db[maname_ps]['Kick-RB']     = {'type':'float', 'value':0.0, 'prec':8, 'unit':'rad'}
#             #     db[maname_ps]['KickRef-Mon'] = {'type':'float', 'value':0.0, 'prec':8, 'unit':'rad'}
#             #     db[maname_ps]['Kick-Mon']    = {'type':'float', 'value':0.0, 'prec':8, 'unit':'rad'}
#             # elif func == 'dipole':
#             #     db[maname_ps]['Energy-SP']     = {'type':'float', 'value':0.0, 'prec':3, 'unit':'GeV'}
#             #     db[maname_ps]['Energy-RB']     = {'type':'float', 'value':0.0, 'prec':3, 'unit':'GeV'}
#             #     db[maname_ps]['EnergyRef-Mon'] = {'type':'float', 'value':0.0, 'prec':3, 'unit':'GeV'}
#             #     db[maname_ps]['Energy-Mon']    = {'type':'float', 'value':0.0, 'prec':3, 'unit':'GeV'}
#         return db
