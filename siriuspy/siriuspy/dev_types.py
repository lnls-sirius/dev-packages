# This module contains data that should be in accordance with databases in the CCDB
# Ideally this module should consume online data from the CCDB service, instead of replicating
# it here. Implementation needed !!!

# this should replicate info in the CCDB machine application

from siriuspy.namedtuple import DevicePropDB as _DevicePropDB


enumeration_types = _namedtuple.EnumTypes(
    OffOnTyp      = ('Off', 'On'),
    OffOnWaitTyp  = ('Off', 'On', 'Wait'),
    DsblEnblTyp   = ('Dsbl', 'Enbl'),
    PSOpModeTyp   = ('SlowRef', 'FastRef', 'WfmRef', 'SigGen'),
    RmtLocTyp     = ('Remote', 'Local'),
    SOFBOpModeTyp = ('Off', 'AutoCorr', 'MeasRespMat'),)


dev_ps_magnet = (
    _DevicePropDB(name='Reset-Cmd',    type='int',   value=0),
    _DevicepropDB(name='CtrlMode-Mon', type='enum',  enums=enum_types.RmtLocTyp, value=enum_types.RmtLocTyp.index('Remote')),
    _DevicepropDB(name='PwrState-Sel', type='enum',  enums=enum_types.OffOnTyp,  value=enum_types.OffOnTyp.index('On')),
    _DevicepropDB(name='PwrState-Sts', type='enum',  enums=enum_types.OffOnTyp,  value=enum_types.OffOnTyp.index('On')),
    _DevicepropDB(name='OpMode-Sel',   type='enum',  enums=enum_types.PSOpMode,  value=enum_types.PSOpMode.index('SlowRef')),
    _DevicepropDB(name='OpMode-Sts',   type='enum',  enums=enum_types.PSOpMode,  value=enum_types.PSOpMode.index('SlowRef')),
    _DevicepropDB(name='Current-SP',   type='float', value=0.0, prec=4, unit='A'),)


def get_device_database(dev):
    database = {}
    for prop in dev:
        db = prop._asdict()
        name = db.pop('name')
        keys,values = db.keys(), db.values()
        for key in keys:
            if db[key] is None:
                db.pop(key)
        database[name] = db

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
        'PwrState-Sel': {'type':'enum', 'enums':enum_types.OffOnTyp, 'value':1, 'unit': ''},
        'PwrState-Sts': {'type':'enum', 'enums':enum_types.OffOnTyp, 'value':1, 'unit': ''},
        'Current-RB':   {'type':'float', 'value':0.0, 'prec':4, 'unit': 'A'},
        'Current-SP':   {'type':'float', 'value':0.0, 'prec':4, 'unit': 'A', 'lolim':0, 'hilim':500},
        'CtrlMode-Mon': {'type':'enum', 'enums':enum_types['RmtLocTyp'], 'value':0, 'unit': ''},
        'OpMode-Sel':   {'type':'enum', 'enums':enum_types['PSOpModeTyp'], 'value':0, 'unit': ''},
        'OpMode-Sts':   {'type':'enum', 'enums':enum_types['PSOpModeTyp'], 'value':0, 'unit': ''},
    }
    return properties
