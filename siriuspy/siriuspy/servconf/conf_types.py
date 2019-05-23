"""Configuration Type Module."""

import importlib as _importlib
import copy as _copy
import numpy as _np
import siriuspy.servconf.types as _types

# NOTE: values for key string labels ending with char '*' have not their
#       sizes compared with a reference if their lists or tuples!

# NOTE: cannot use tuple values in configuration dictionaries since conversion
#       through json looses track of tuple|list type.

_config_types_dict = None
_config_types_check = None
_config_types_checklength = None
_int_types = {int}
for k, tp in _np.typeDict.items():
    if isinstance(k, str) and k.startswith('int'):
        _int_types.add(tp)

_float_types = {float}
for k, tp in _np.typeDict.items():
    if isinstance(k, str) and k.startswith('float'):
        _float_types.add(tp)


def get_config_types():
    """Return list of configuration types."""
    if _config_types_dict is None:
        _init_config_types_dict()
    return tuple(_config_types_dict.keys())


def get_config_type_template(ctype):
    """Return value of a configuration type."""
    if _config_types_dict is None:
        _init_config_types_dict()
    value = _config_types_dict[ctype]
    return _copy.deepcopy(value)


def check_value(config_type, value):
    """Check whether values data corresponds to a configuration type."""
    if _config_types_dict is None:
        _init_config_types_dict()
    ref_value = _config_types_dict[config_type]
    if _config_types_check[config_type]:
        if _config_types_checklength[config_type]:
            return recursive_check(ref_value, value)
        return recursive_check(ref_value, value, checklength=False)
    return True


def _init_config_types_dict():
    global _config_types_dict, _config_types_check, _config_types_checklength
    _config_types_dict = dict()
    _config_types_check = dict()
    _config_types_checklength = dict()
    for ct_name in _types._ctypes:
        ctm = _importlib.import_module('siriuspy.servconf.types.' + ct_name)
        ct = ctm.get_dict()
        config_type_name = ct['config_type_name']
        _config_types_dict[config_type_name] = ct['value']
        _config_types_check[config_type_name] = ct.get('check', True)
        _config_types_checklength[config_type_name] = ct.get(
            'checklength', True)


# NOTE: It would be better if this method raised an error with a message
#       specifying the name of the PV which is incompatible.
def recursive_check(ref_value, value, checklength=True):
    tps = {type(ref_value), type(value)}
    if len(tps) > len(tps - _int_types) > 0:
        # print('h1')
        return False
    elif len(tps) > len(tps - _float_types) > 0:
        # print('h2')
        return False
    elif isinstance(ref_value, dict):
        if checklength and len(value) != len(ref_value):
            # print('h3')
            return False
        for k, v in value.items():
            if k not in ref_value and checklength:
                # print('h4')
                return False
            if k in ref_value:
                v_ref = ref_value[k]
                if isinstance(k, str) and k.endswith('*'):
                    checked = recursive_check(v_ref, v, checklength=False)
                else:
                    checked = recursive_check(v_ref, v, checklength)
                if not checked:
                    # print('h5')
                    return False
    elif isinstance(ref_value, (list, tuple, _np.ndarray)):
        if checklength and len(ref_value) != len(value):
            # print('h6')
            return False
        for i in range(min(len(value), len(ref_value))):
            checked = recursive_check(value[i], ref_value[i], checklength)
            if not checked:
                # print('h7')
                return False
    return True
