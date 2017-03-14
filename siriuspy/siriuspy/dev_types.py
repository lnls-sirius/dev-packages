# This module should contain data that should be in accordance with databases in the CCDB
# Ideally this module should consume online data from the CCDB service, instead of replicating
# it here. Implementation needed !!!

# this should replicate info in the CCDB machine application
def get_enum_types():
    enum_types = {
        'OffOnTyp'      : ('Off','On'),
        'OffOnWaitTyp'  : ('Off','On','Wait'),
        'DsblEnblTyp'   : ('Dsbl','Enbl'),
        'PSOpModeTyp'   : ('SlowRef','FastRef','WfmRef','SigGen'),
        'RmtLocTyp'     : ('Remote','Local'),
        'SOFBOpModeTyp' : ('Off','AutoCorr','MeasRespMat'),
    }
    return enum_types

# this should replicate info in the CCDB machine application
def get_magnet_ps_properties():
    enum_types = get_enum_types()
    properties = {
        'Reset-Cmd':    {'type':'int', 'value':0},
        'PwrState-Sel': {'type':'enum', 'enums':enum_types['OffOnTyp'], 'value':1, 'unit': ''},
        'PwrState-Sts': {'type':'enum', 'enums':enum_types['OffOnTyp'], 'value':1, 'unit': ''},
        'Current-RB':   {'type':'float', 'value':0.0, 'prec':4, 'unit': 'A'},
        'Current-SP':   {'type':'float', 'value':0.0, 'prec':4, 'unit': 'A'},
        'CtrlMode-Mon': {'type':'enum', 'enums':enum_types['RmtLocTyp'], 'value':0, 'unit': ''},
        'OpMode-Sel':   {'type':'enum', 'enums':enum_types['PSOpModeTyp'], 'value':0, 'unit': ''},
        'OpMode-Sts':   {'type':'enum', 'enums':enum_types['PSOpModeTyp'], 'value':0, 'unit': ''},
    }
    return properties
