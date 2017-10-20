"""Configuration Type Module."""

import copy as _copy

_config_types = (
    # si-tunes
    {'config_type_name': 'si-tunes',
     'value': {'tunex': 0.0, 'tuney': 0.0, },
     },
    # bo-tunes
    {'config_type_name': 'bo-tunes',
     'value': {'tunex': 0.0, 'tuney': 0.0, },
     },
)

_config_types_dict = None


def get_config_types():
    """Return list of configuration types."""
    if _config_types_dict is None:
        _init_config_types_dict()
    return tuple(_config_types_dict.keys())


def get_config_type_value(ctype):
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
    for ct in _config_types:
        config_type_name = ct['config_type_name']
        _config_types_dict[config_type_name] = ct['value']


def _recursive_check(ref_value, value):
    # should be allow float - int automatic castings ?
    if type(ref_value) != type(value):
        return False
    if type(ref_value) == dict:
        if len(ref_value) != len(value):
            return False
        for k, v in value.items():
            if k not in ref_value:
                return False
            v_ref = ref_value[k]
            checked = _recursive_check(v_ref, v)
            if not checked:
                return False
    elif type(ref_value) in (list, tuple, ):
        if len(ref_value) != len(value):
            return False
        for i in range(len(value)):
            checked = _recursive_check(value[i], ref_value[i])
            if not checked:
                return False
    return True
