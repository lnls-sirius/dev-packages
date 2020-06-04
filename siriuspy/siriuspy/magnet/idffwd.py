"""Insertion Device Feedforward Correction Classes."""

import numpy as _np

from ..search import IDSearch as _IDSearch
from ..search import MASearch as _MASearch


class APUFFWDCalc:
    """."""

    def __init__(self, idname):
        """."""
        # get correctors names
        self._psnames_orb = _IDSearch.conv_idname_2_orbitcorr(idname)
        # NOTE: assumes same number of CHs and CVs
        self._nr_chs = len(self._psnames_orb) // 2
        self._nr_cvs = self._nr_chs

        # get corr spos
        self._orbcorr_spos = self._get_corr_spos()

        # get orbit fftable from idname:
        self._orbitffwd = _IDSearch.conv_idname_2_orbitffwd(idname)

    @property
    def nr_chs(self):
        """Return number of orbit CH correctors."""
        return self._nr_chs

    @property
    def nr_cvs(self):
        """Return number of orbit CV correctors."""
        return self._nr_cvs

    @property
    def psnames_orbitcorr(self):
        """Return orbit corrector names."""
        return self._psnames_orb

    def conv_phase_2_orbcorr_currents(self, phase):
        """Return orbit correctors currents for a given ID phase."""
        ffwd = self._orbitffwd.interp_curr2mult(phase)
        chs = [ffwd['normal'][i] for i in range(self.nr_chs)]
        cvs = [ffwd['skew'][i] for i in range(self.nr_cvs)]
        currents = _np.array(chs + cvs)
        return currents

    def conv_posang_2_orbcorr_kicks(
            self, posx=0, angx=0, posy=0, angy=0):
        """Return orbit correctors currents for bumps and angles.

        Geometry (a courtesy of F. de Sá):

        >----------------> ebeam direction >---------------->
        C1|C1      C2|C2                     C3|C3      C4|C4
          |---len1---|----len2----|----len2----|---len1---|

        """
        def calc_kicks(pos, ang):
            # angle bump
            theta = _np.atan(len2/len1 * _np.tan(ang/1e6)) * 1e6
            corrs = [-theta, theta + ang, -theta - ang, theta]
            # offset bump
            theta = _np.atan(pos / 1e6 / len1) * 1e6
            corrs[0] += theta
            corrs[1] -= theta
            corrs[2] -= theta
            corrs[3] += theta
            return corrs

        spos = self._orbcorr_spos
        len1 = spos[1] - spos[0]
        len2 = 0.5*(spos[2] - spos[1])
        kicks = calc_kicks(posx, angx) + calc_kicks(posy, angy)
        return _np.asarray(kicks)



    # --- private methods ---

    def _get_corr_spos(self):
        manames = [psname.replace(':PS-', ':MA-') for
                   psname in self._psnames_orb]
        spos = _MASearch.get_mapositions(names=manames)
        return spos
