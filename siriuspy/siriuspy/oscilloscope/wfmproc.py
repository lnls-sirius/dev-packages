"""."""

import numpy as _np


class WfmProcess:
    """."""

    def __init__(self, tim, wfm):
        """."""
        self._tim = tim
        self._wfm = wfm
        (
            self._wfm_maxmin,
            (self._domain_tim, self._domain_idx)
        ) = WfmProcess.calc_basic_params(self._tim, self._wfm)

    @property
    def tim(self):
        """[s]."""
        return self._tim

    @property
    def wfm(self):
        """[V]."""
        return self._wfm

    @property
    def wfm_maxmin(self):
        """."""
        return self._wfm_maxmin

    @property
    def wfm_idx_max(self):
        """."""
        return self._domain_idx[0]

    @property
    def wfm_idx_fwhm(self):
        """."""
        return self._domain_idx[1]

    @property
    def wfm_tim_max(self):
        """."""
        return self._domain_tim[0]

    @property
    def wfm_tim_fwhm(self):
        """."""
        return self._domain_tim[1]

    def fit_linear_coeffs(self, normalized_vectors):
        """."""
        mat_a = _np.column_stack(normalized_vectors)
        coeffs, residues, rank, s = _np.linalg.lstsq(
            mat_a, self._wfm, rcond=None
        )
        return coeffs, residues, rank, s

    @staticmethod
    def calc_basic_params(tim, wfm):
        """."""
        min_wfm = _np.min(wfm)
        max_wfm = _np.max(wfm)
        max_idx = _np.argmax(wfm)
        max_tim = tim[max_idx]

        left_side = wfm[:max_idx]
        right_side = wfm[max_idx:]

        left_idx = _np.abs(left_side - max_wfm/2).argmin()
        right_idx = _np.abs(right_side - max_wfm/2).argmin() + max_idx

        fwhm_idx = right_idx - left_idx
        fwhm_tim = tim[right_idx] - tim[left_idx]

        wfm_maxmin = (max_wfm, min_wfm)
        domain_idx = (max_idx, fwhm_idx)
        domain_tim = (max_tim, fwhm_tim)

        return wfm_maxmin, domain_tim, domain_idx
