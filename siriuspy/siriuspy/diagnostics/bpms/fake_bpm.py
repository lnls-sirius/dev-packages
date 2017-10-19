import numpy as _np
import copy as _copy
from .pvs import pvs_definitions as pvDB


_TYPES = {'float': float, 'int': int, 'bool': int, 'string': str,
          'enum': int, 'char': str}

_wr_prop = """
@property
def {0}_{1}(self):
    return _copy.deepcopy(self._{0}_{1})

@{0}_{1}.setter
def {0}_{1}(self, new_val):
    count = pvDB['{2}'].get('count', 1)
    tp = _TYPES[pvDB['{2}']['type']]
    if count > 1:
        self._{0}_{1} = _np.array(new_val, dtype=tp)
    else:
        self._{0}_{1} = tp(new_val)
"""

_sp_prop = """
@property
def {0}_{1}(self):
    return _copy.deepcopy(self._{0}_{1})

@{0}_{1}.setter
def {0}_{1}(self, new_val):
    count = pvDB['{3}'].get('count', 1)
    tp =  _TYPES[pvDB['{3}']['type']]
    if count > 1:
        self._{0}_{1} = _np.array(new_val, dtype=tp)
        self._{0}_{2} = self._{0}_{1}
    else:
        self._{0}_{1} = tp(new_val)
        self._{0}_{2} = self._{0}_{1}
"""

_sel_prop = """
@property
def {0}_{1}(self):
    return _copy.deepcopy(self._{0}_{1})

@{0}_{1}.setter
def {0}_{1}(self, new_val):
    if new_val in pvDB['{3}']['enums']:
        self._{0}_{1} = pvDB['{3}']['enums'].index(new_val)
        self._{0}_{2} = self._{0}_{1}
    elif int(new_val) < len(pvDB['{3}']['enums']):
        self._{0}_{1} = int(new_val)
        self._{0}_{2} = self._{0}_{1}
"""

_rb_prop = """
@property
def {0}_{1}(self):
    return _copy.deepcopy(self._{0}_{1})
"""


class BPMFake:

    def __init__(self, bpm_name):
        for pv, db in pvDB.items():
            prop = pv.lower().replace('-', '_').replace('.', '')
            setattr(self, '_' + prop, db.get('value', 0))

    for pv, db in pvDB.items():
        prop = pv.lower().replace('-', '_').replace('.', '')
        prop = prop.split('_')
        suf = prop[1] if len(prop) > 1 else ''
        prop = prop[0]
        if suf == 'sp':
            exec(_sp_prop.format(prop, suf, 'rb', pv))
        elif suf == 'sel':
            exec(_sel_prop.format(prop, suf, 'sts', pv))
        elif suf in ('rb', 'sts'):
            exec(_rb_prop.format(prop, suf))
        else:
            if prop.endswith('span'):
                exec(_wr_prop.format(prop, suf, pv))
            else:
                exec(_rb_prop.format(prop, suf))
