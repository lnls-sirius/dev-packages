"""Booster ramp configuration definition."""
import copy as _copy
from siriuspy.csdevice.pwrsupply import max_wfmsize as \
    _max_wfmsize


_ref_wfm_array = [0.0 for _ in range(_max_wfmsize)]


def get_dict():
    """Return a dict with ramp settings."""
    module_name = __name__.split('.')[-1]

    _dict = {
        'config_type_name': module_name,
        'value': _copy.deepcopy(_value)
    }

    return _dict


_value = {
    # --- dipole ---
    'BO-Fam:MA-B:WfmData-SP': _ref_wfm_array,
    # --- quadrupole ---
    'BO-Fam:MA-QF:WfmData-SP': _ref_wfm_array,
    'BO-Fam:MA-QD:WfmData-SP': _ref_wfm_array,
    # --- sextupole ---
    'BO-Fam:MA-SF:WfmData-SP': _ref_wfm_array,
    'BO-Fam:MA-SD:WfmData-SP': _ref_wfm_array,
    # --- quadrupole skew ---
    'BO-02D:MA-QS:WfmData-SP': _ref_wfm_array,
    # --- horizontal correctors ---
    'BO-01U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-03U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-05U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-07U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-09U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-11U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-13U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-15U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-17U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-19U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-21U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-23U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-25U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-27U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-29U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-31U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-33U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-35U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-37U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-39U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-41U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-43U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-45U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-47U:MA-CH:WfmData-SP': _ref_wfm_array,
    'BO-49D:MA-CH:WfmData-SP': _ref_wfm_array,
    # --- vertical correctors ---
    'BO-01U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-03U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-05U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-07U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-09U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-11U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-13U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-15U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-17U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-19U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-21U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-23U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-25U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-27U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-29U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-31U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-33U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-35U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-37U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-39U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-41U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-43U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-45U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-47U:MA-CV:WfmData-SP': _ref_wfm_array,
    'BO-49U:MA-CV:WfmData-SP': _ref_wfm_array,
}
