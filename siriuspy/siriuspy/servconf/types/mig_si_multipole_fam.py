"""Booster ramp configuration definition."""
import copy as _copy
from siriuspy.servconf.types.rmp_bo_ps import _ref_wfm_array


def get_dict():
    """Return a dict with ramp settings."""
    module_name = __name__.split('.')[-1]

    _dict = {
        'config_type_name': module_name,
        'value': _copy.deepcopy(_value)
    }

    return _dict


_value = {
    'SI-Fam:MA-Q1:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-Q2:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-Q3:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-Q4:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-QFA:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-QFB:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-QFP:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-QDA:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-QDB1:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-QDB2:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-QDP1:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-QDP2:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDA0:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDA1:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDA2:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDA3:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDB0:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDB1:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDB2:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDB3:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDP0:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDP1:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDP2:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SDP3:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SFA0:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SFA1:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SFA2:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SFB0:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SFB1:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SFB2:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SFP0:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SFP1:WfmData-Sel': _ref_wfm_array,
    'SI-Fam:MA-SFP2:WfmData-Sel': _ref_wfm_array,
}
