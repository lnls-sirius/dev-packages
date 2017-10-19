import numpy as _np
import copy as _copy
from epics import PV as _PV
from .pvs import pvs_definitions as pvDB


_TYPES = {'float': float, 'int': int, 'bool': int, 'string': str,
          'enum': int, 'char': str}

_sp_prop = """
@property
def {0}_{1}(self):
    if self.pvs['{2}'].connected:
        return _copy.deepcopy(self.pvs['{2}'].value)

@{0}_{1}.setter
def {0}_{1}(self, new_val):
    if not self.pvs['{2}'].connected:
        return
    count = pvDB['{2}'].get('count', 1)
    tp = _TYPES[pvDB['{2}']['type']]
    if count > 1:
        self.pvs['{2}'].value = _np.array(new_val, dtype=tp)
    else:
        self.pvs['{2}'].value = tp(new_val)
"""

_sel_prop = """
@property
def {0}_{1}(self):
    if self.pvs['{2}'].connected:
        return _copy.deepcopy(self.pvs['{2}'].value)

@{0}_{1}.setter
def {0}_{1}(self, new_val):
    if not self.pvs['{2}'].connected:
        return
    if new_val in pvDB['{2}']['enums']:
        self.pvs['{2}'].value = pvDB['{2}']['enums'].index(new_val)
    elif int(new_val) < len(pvDB['{2}']['enums']):
        self.pvs['{2}'].value = int(new_val)
"""

_rb_prop = """
@property
def {0}_{1}(self):
    if self.pvs['{2}'].connected:
        return _copy.deepcopy(self.pvs['{2}'].value)
"""


class BPMEpics:

    def __init__(self, bpm_name, prefix=''):
        for pv, db in pvDB.items():
            self.pvs[pv] = _PV(prefix+bpm_name+':'+pv)

    for pv, db in pvDB.items():
        prop = pv.lower().replace('-', '_').replace('.', '')
        prop = prop.split('_')
        suf = prop[1] if len(prop) > 1 else ''
        prop = prop[0]
        if suf == 'sp':
            exec(_sp_prop.format(prop, suf, pv))
        elif suf == 'sel':
            exec(_sel_prop.format(prop, suf, pv))
        elif suf in ('rb', 'sts'):
            exec(_rb_prop.format(prop, suf, pv))
        else:
            if prop.endswith('span'):
                exec(_sp_prop.format(prop, suf, pv))
            else:
                exec(_rb_prop.format(prop, suf, pv))
