"""Configuration Type Module."""

import importlib as _importlib
import siriuspy.servconf.types as _types
import copy as _copy

# NOTE: values for key string labels ending with char '*' have not their
#       sizes compared with a reference if their lists or tuples!

_config_types_dict = None


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
    return _recursive_check(ref_value, value)


def _init_config_types_dict():
    global _config_types_dict
    _config_types_dict = {}
    for ct_name in _types._ctypes:
        ctm = _importlib.import_module('siriuspy.servconf.types.' + ct_name)
        ct = ctm.get_dict()
        config_type_name = ct['config_type_name']
        _config_types_dict[config_type_name] = ct['value']


def _recursive_check(ref_value, value, same_length=True):
    if type(ref_value) != type(value):
        return False
    if type(ref_value) == dict:
        if len(ref_value) != len(value):
            return False
        for k, v in value.items():
            if k not in ref_value:
                return False
            v_ref = ref_value[k]
            if isinstance(k, str) and k.endswith('*'):
                checked = _recursive_check(v_ref, v, same_length=False)
            else:
                checked = _recursive_check(v_ref, v, same_length)
            if not checked:
                return False
    elif type(ref_value) in (list, tuple, ):
        if len(ref_value) != len(value):
            return False
        for i in range(len(value)):
            checked = _recursive_check(value[i], ref_value[i], same_length)
            if not checked:
                return False
    return True
