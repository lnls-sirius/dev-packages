import time as _time
import datetime as _datetime


def get_timestamp():
    t0 = _time.time()
    st = _datetime.datetime.fromtimestamp(t0).strftime('%Y-%m-%d-%H:%M:%S')
    st = st + '.{0:03d}'.format(int(1000*(t0-int(t0))))
    return st


def get_prop_types():
    prop_types = {
        'RB'  : {'read':True,  'write':False, 'enum':False},
        'SP'  : {'read':True,  'write':True,  'enum':False},
        'Sel' : {'read':True,  'write':True,  'enum':True},
        'Sts' : {'read':True,  'write':False, 'enum':True},
        'Cmd' : {'read':False, 'write':True,  'enum':False},
    }
    return prop_types


def get_prop_suffix(prop):
    if prop[-3:] == '-RB': return 'RB'
    if prop[-3:] == '-SP': return 'SP'
    if prop[-4:] == '-Sel': return 'Sel'
    if prop[-4:] == '-Sts': return 'Sts'
    if prop[-4:] == '-Mon': return 'Mon'
    if prop[-4:] == '-Cmd': return 'Cmd'
    return None


def get_enum_types():
    enums = {
        'OffOnTyp' : ('Off','On'),
        'OffOnWaitTyp' : ('Off','On','Wait'),
    }
    return enums
