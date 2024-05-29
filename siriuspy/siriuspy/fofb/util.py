import numpy as _np
from .csdev import HLFOFBConst as _Const
from ..devices import FamFOFBControllers as _FamFOFBCtrls, \
        FamFastCorrs as _FamFastCorrs, PowerSupplyFC as _PS


def set_default_psconfig_mat(option=None):
    """Set corrector accumulator filter.

    Args:
        option (str): either 'Switching' or 'Unit'.
            If None, we consider option = 'Unit'.

    Returns:
        std_psconfig_mat (numpy.ndarray):
            PS Configuration matrix.

    """

    _const = _Const()
    _llfofb_dev = _FamFOFBCtrls()
    _ps = _PS()

    corrnames = _const.ch_names + _const.cv_names
    _corrs_dev = _FamFastCorrs(corrnames)

    num_biquads = _llfofb_dev.fofbacc_filter_num_biquads
    unit = _const.FILTER_UNIT
    sw2 = _const.FILTER_SW_2
    sw4 = _const.FILTER_SW_4

    if option == 'Unit' or option is None:
        _acc_filter_coeffs = num_biquads * unit

    if option == 'Switching':
        _acc_filter_coeffs = sw2 + sw4 + (num_biquads - 2) * unit

    else:
        raise ValueError('Option must be Unit or Switching.')

    _corr_currloop_kp = _ps.currloop_kp
    _corr_currloop_ti = _ps.currloop_ti
    _corr_accfilter_gain = _corrs_dev.fofbacc_filter_gain

    if not _const.psconfig_nr_coeffs_columns == num_biquads*5:
        raise ValueError('Number of biquads does not match number of filter\
                         coefficients - each biquad must have 5 coefficients.')

    std_psconfig_mat = _np.zeros(
        (_const.nr_chcv, _const.psconfig_nr_coeffs_columns + 3),
        dtype=float
    )
    std_psconfig_mat[:, 0] = _corr_currloop_kp
    std_psconfig_mat[:, 1] = _corr_currloop_ti
    std_psconfig_mat[:, 2] = _corr_accfilter_gain
    std_psconfig_mat[:, 3:] = _acc_filter_coeffs

    return std_psconfig_mat
