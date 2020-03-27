"""Configuration Type Module."""

import importlib as _importlib
import copy as _copy
import numpy as _np

from . import types as _types

# NOTE: values for key string labels ending with char '*' have not their
#       sizes compared with a reference if their lists or tuples!

# NOTE: cannot use tuple values in configuration dictionaries since conversion
#       through json looses track of tuple|list type.

_CONFIG_TYPES_DICT = None
_CONFIG_TYPES_CHECK = None
_INT_TYPES = {int}
_FLOAT_TYPES = {float}


for key, typ in _np.typeDict.items():
    if isinstance(key, str) and key.startswith('int'):
        _INT_TYPES.add(typ)


for key, typ in _np.typeDict.items():
    if isinstance(key, str) and key.startswith('float'):
        _FLOAT_TYPES.add(typ)


def get_config_types():
    """Return list of configuration types."""
    if _CONFIG_TYPES_DICT is None:
        _init_CONFIG_TYPES_DICT()
    return tuple(_CONFIG_TYPES_DICT.keys())


def get_template(config_type):
    """Return value of a configuration type."""
    if _CONFIG_TYPES_DICT is None:
        _init_CONFIG_TYPES_DICT()
    value = _CONFIG_TYPES_DICT.get(config_type, dict())
    return _copy.deepcopy(value)


def check_value(config_type, value):
    """Check whether values data corresponds to a configuration type."""
    if _CONFIG_TYPES_DICT is None:
        _init_CONFIG_TYPES_DICT()
    ref_value = _CONFIG_TYPES_DICT[config_type]
    if _CONFIG_TYPES_CHECK[config_type]:
        return _recursive_check(ref_value, value)
    return True


def _init_CONFIG_TYPES_DICT():
    global _CONFIG_TYPES_DICT, _CONFIG_TYPES_CHECK
    _CONFIG_TYPES_DICT = dict()
    _CONFIG_TYPES_CHECK = dict()
    for ct_name in _types.CONFIG_TYPES:
        ctm = _importlib.import_module(
            'siriuspy.clientconfigdb.types.' + ct_name)
        ct = ctm.get_dict()
        config_type_name = ct['config_type_name']
        _CONFIG_TYPES_DICT[config_type_name] = ct['value']
        _CONFIG_TYPES_CHECK[config_type_name] = ct.get('check', True)


# NOTE: It would be better if this method raised an error with a message
#       specifying the name of the PV which is incompatible.
def _recursive_check(ref_value, value, checklength=True):
    tps = {type(ref_value), type(value)}
    if len(tps) > len(tps - _INT_TYPES) > 0:
        # print('h1')
        return False
    elif len(tps) > len(tps - _FLOAT_TYPES) > 0:
        # print('h2')
        return False
    elif isinstance(ref_value, dict):
        if checklength and len(value) != len(ref_value):
            # print('h3')
            return False
        for key, val in value.items():
            if key not in ref_value and checklength:
                # print('h4')
                return False
            if key in ref_value:
                v_ref = ref_value[key]
                if isinstance(key, str) and key.endswith('*'):
                    checked = _recursive_check(v_ref, val, checklength=False)
                else:
                    checked = _recursive_check(v_ref, val, checklength)
                if not checked:
                    # print('h5')
                    return False
    elif isinstance(ref_value, (list, tuple, _np.ndarray)):
        if checklength and len(ref_value) != len(value):
            # print('h6')
            return False
        for i in range(min(len(value), len(ref_value))):
            checked = _recursive_check(value[i], ref_value[i], checklength)
            if not checked:
                # print('h7')
                return False
    return True
