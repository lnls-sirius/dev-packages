import numpy as _np
from .csdev import HLFOFBConst as _Const
from ..devices import FamFOFBControllers as _FamFOFBCtrls, \
        FamFastCorrs as _FamFastCorrs


def get_default_psconfig_mat(option=None):
    """Set corrector accumulator filter.

    Args:
        option (str): either 'Switching' or 'Unit'.
            If None, we consider option = 'Unit'.

    Returns:
        mat (numpy.ndarray):
            PS Configuration matrix.

    """

    _const = _Const()
    _llfofb_dev = _FamFOFBCtrls()

    corrnames = _const.ch_names + _const.cv_names
    _corrs_dev = _FamFastCorrs(corrnames)

    num_biquads = _llfofb_dev.fofbacc_filter_num_biquads
    unit = _const.FILTER_UNIT
    sw2 = _const.FILTER_SW_2
    sw4 = _const.FILTER_SW_4
    unit_gain = _np.ones(_const.nr_chcv, dtype=float)

    if option == 'Unit' or option is None:
        _acc_filter_coeffs = num_biquads * unit

    elif option == 'Switching':
        _acc_filter_coeffs = sw2 + sw4 + (num_biquads - 2) * unit

    else:
        raise ValueError('Option must be Unit or Switching.')

    _corr_currloop_kp = _corrs_dev.currloop_kp
    _corr_currloop_ki = _corrs_dev.currloop_ki

    mat = _np.zeros(
        (_const.nr_chcv, _const.psconfig_nr_coeffs_columns +
         _const.PSCONFIG_COEFF_FIRST_COL),
        dtype=float
    )
    mat[:, _const.PSCONFIG_KP_COL] = _corr_currloop_kp
    mat[:, _const.PSCONFIG_KI_COL] = _corr_currloop_ki
    mat[:, _const.PSCONFIG_FILTER_GAIN_COL] = unit_gain
    mat[:, _const.PSCONFIG_COEFF_FIRST_COL:] = _acc_filter_coeffs

    return mat
