"""Configuration Type Module."""

import importlib as _importlib
import siriuspy.servconf.types as _types
import copy as _copy

# NOTE: values for key string labels ending with char '*' have not their
#       sizes compared with a reference if their lists or tuples!

# NOTE: cannot use tuple values in configuration dictionaries since conversion
#       through json looses track of tuple|list type.

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
    return recursive_check(ref_value, value)


def _init_config_types_dict():
    global _config_types_dict
    _config_types_dict = {}
    for ct_name in _types._ctypes:
        ctm = _importlib.import_module('siriuspy.servconf.types.' + ct_name)
        ct = ctm.get_dict()
        config_type_name = ct['config_type_name']
        _config_types_dict[config_type_name] = ct['value']


def recursive_check(ref_value, value, checklength=True):
    if type(ref_value) != type(value):
        # print('h1')
        return False
    if type(ref_value) == dict:
        for k, v in value.items():
            if k not in ref_value and checklength:
                # print('h3')
                return False
            if k in ref_value:
                v_ref = ref_value[k]
                if isinstance(k, str) and k.endswith('*'):
                    checked = recursive_check(v_ref, v, checklength=False)
                else:
                    checked = recursive_check(v_ref, v, checklength)
                if not checked:
                    # print('h4')
                    return False
    elif type(ref_value) in (list, tuple, ):
        if checklength and len(ref_value) != len(value):
            # print('h5')
            return False
        for i in range(min(len(value), len(ref_value))):
            checked = recursive_check(value[i], ref_value[i], checklength)
            if not checked:
                # print('h6')
                return False
    return True
