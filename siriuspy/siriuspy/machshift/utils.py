"""Machine shift utils."""

import numpy as _np


# This solution is a simplified version of scipy.interpolate.interp1d for
# interpolation of kind 'previous' with fill_value='extrapolate' option
def interp1d_previous(x_org, y_org, x_new):
    """interp1d to previous."""
    x_new = _np.asarray(x_new)
    x_org = _np.asarray(x_org).ravel()
    y_org = _np.asarray(y_org)

    # Get index of left value
    x_new_indices = _np.searchsorted(
        _np.nextafter(x_org, -_np.inf), x_new, side='left')

    # Clip x_new_indices so that they are within the range of x_org indices.
    x_new_indices = x_new_indices.clip(1, len(x_org)).astype(_np.intp)

    # Calculate the actual value for each entry in x_new.
    y_new = y_org[x_new_indices-1]

    return y_new


# Version using scipy.interpolate.interp1d
# from scipy.interpolate import interp1d as _interp1d
# def _interp1d_previous(x_org, y_org, x_new):
#     """interp1d to previous."""
#     fun = _interp1d(x_org, y_org, 'previous', fill_value='extrapolate')
#     y_new = fun(x_new)
#     return y_new
