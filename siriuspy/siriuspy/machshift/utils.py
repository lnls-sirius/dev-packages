"""Machine shift utils."""

import os as _os

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


class HandleMachShiftFile:
    """Class to handle machine shift file."""

    def __init__(self):
        """Init."""
        self.fpath = '/home/sirius/iocs-log/as-ap-machshift/'
        self.fname = self.fpath + 'last-mach-shift.txt'

    def get_machshift(self):
        """Get last shift from file."""
        if _os.path.isfile(self.fname):
            with open(self.fname, 'r') as fil:
                machshift = fil.read().strip('\n')
        else:
            _os.makedirs(self.fpath, exist_ok=True)
            machshift = 1  # Commissioning
            with open(self.fname, 'w+') as fil:
                fil.write(machshift)
        return int(machshift)

    def set_machshift(self, machshift):
        """Set last shift in file."""
        if not isinstance(machshift, int):
            raise TypeError("'machshift' must be an int.")
        with open(self.fname, 'w+') as fil:
            fil.write(str(machshift))
