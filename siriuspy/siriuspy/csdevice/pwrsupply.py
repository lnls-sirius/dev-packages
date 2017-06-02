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
