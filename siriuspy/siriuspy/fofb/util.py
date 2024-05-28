import numpy as _np
from .csdev import HLFOFBConst as _Const
from ..devices import FamFOFBControllers as _FamFOFBCtrls, \
        FamFastCorrs as _FamFastCorrs, PowerSupplyFC as _PS


def set_default_psconfig_mat(option):
    """Set corrector accumulator filter."""

    _const = _Const()
    _llfofb_dev = _FamFOFBCtrls()
    _ps = _PS()

    corrnames = _const.ch_names + _const.cv_names
    _corrs_dev = _FamFastCorrs(corrnames)

    num_biquads = _llfofb_dev.fofbacc_filter_num_biquads
    unit = _const.FILTER_UNIT
    sw2 = _const.FILTER_SW_2
    sw4 = _const.FILTER_SW_4

    if option == 'Unit':
        filter_coeffs = num_biquads * unit

    if option == 'Switching':
        filter_coeffs = sw2 + sw4 + (num_biquads - 2) * unit

    _corr_currloop_kp = _ps.currloop_kp
    _corr_currloop_ti = _ps.currloop_ti
    _corr_accfilter_gain = _corrs_dev.fofbacc_filter_gain
    std_psconfig_mat = _np.zeros(
            (_const.nr_chcv, _const.psconfig_nr_coeffs_columns + 3),
            dtype=float)
    std_psconfig_mat[:, 0] = _corr_currloop_kp
    std_psconfig_mat[:, 1] = _corr_currloop_ti
    std_psconfig_mat[:, 2] = _corr_accfilter_gain
    std_psconfig_mat[:, 3:] = filter_coeffs

    return std_psconfig_mat
