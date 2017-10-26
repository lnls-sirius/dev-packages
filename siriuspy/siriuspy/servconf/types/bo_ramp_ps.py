"""Booster ramp configuration definition."""
from siriuspy.csdevice.pwrsupply import default_wfmsize
import copy as _copy


def get_dict():
    """Return a dict with ramp settings."""
    module_name = __name__.split('.')[-1]

    _dict = {
        'config_type_name': module_name,
        'value': _copy.deepcopy(_value)
    }

    return _dict


ref_array = list(range(default_wfmsize))
_value = {
    "BO-Fam:MA-B:WfmData-SP": ref_array,
    "BO-Fam:MA-QF:WfmData-SP": ref_array,
    "BO-Fam:MA-QD:WfmData-SP": ref_array,
    "BO-Fam:MA-SF:WfmData-SP": ref_array,
    "BO-Fam:MA-SD:WfmData-SP": ref_array
}
