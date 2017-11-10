"""EXcitation Data."""

import numpy as _np
import siriuspy.servweb as _web
from siriuspy.magnet import util as _util


class ExcitationData:
    """ExcitationData class."""

    def __init__(self, filename_web=None, filename=None, text=None):
        """Init method."""
        self._init()

        if int(filename is not None) + \
           int(text is not None) + \
           int(filename_web is not None) > 1:
            raise Exception('ambiguous constructor arguments')

        if text:
            self._read_text(text)
        elif filename:
            self._read_file(filename)
        else:
            self._read_webs(filename_web)

    def _init(self):

        self.label = ''
        self._harmonics = []
        self._main_multipole_harmonic = None
        self._main_multipole_type = None
        self.column_units = ''
        self.currents = []
        self.multipoles = {}

    # --- properties ---

    @property
    def harmonics(self):
        """Return list with multipole harmonics."""
        return [h for h in self._harmonics]

    @property
    def main_multipole_harmonic(self):
        """Return main multipole."""
        return self._main_multipole_harmonic

    @property
    def main_multipole_type(self):
        """Return string indicating type of main multipoel."""
        return self._main_multipole_type

    @property
    def current_limits(self):
        """Return current limits."""
        return self._current_limits

    # --- public methods ---

    def check_valid_curr(self, value):
        """Check if current is within limits of excitation data."""
        return self.currents[0] <= value <= self.currents[-1]

    def check_valid_mult(self, value, harmonic, multipole_type):
        """Check if multipole is within limits of excitation data."""
        multipoles = self.multipoles[multipole_type.lower()][harmonic]
        return min(multipoles) <= value <= max(multipoles)

    def interp_curr2mult(self, currents):
        """Interpolate multipoles for current values."""
        ct = self.currents
        multipoles = {'normal': {}, 'skew': {}}
        if _np.isscalar(currents):
            currents = _np.array([currents])
            for h in self.harmonics:
                # normal component
                mt = self.multipoles['normal'][h]
                interp = ExcitationData._calc_interp(ct, mt, currents)
                multipoles['normal'][h] = interp[0]
                # skew component
                mt = self.multipoles['skew'][h]
                interp = ExcitationData._calc_interp(ct, mt, currents)
                multipoles['skew'][h] = interp[0]
        else:
            currents = _np.array(currents)
            for h in self.harmonics:
                # normal component
                mt = self.multipoles['normal'][h]
                interp = ExcitationData._calc_interp(ct, mt, currents)
                multipoles['normal'][h] = interp
                # skew component
                mt = self.multipoles['skew'][h]
                interp = ExcitationData._calc_interp(ct, mt, currents)
                multipoles['skew'][h] = interp
        return multipoles

    def interp_mult2curr(self, multipoles, harmonic, multipole_type):
        """Interpolate current from a specific multipole value."""
        # sort correctly tabulated lists
        mt = self.multipoles[multipole_type.lower()][harmonic]
        if mt[-1] <= mt[0]:
            mt = mt[::-1]
            ct = self.currents[::-1]
        else:
            ct = self.currents
        # do conversion
        if _np.isscalar(multipoles):
            multipoles = _np.array([multipoles])
            interp = ExcitationData._calc_interp(mt, ct, multipoles)
            currents = interp[0]
        else:
            multipoles = _np.array(multipoles)
            interp = ExcitationData._calc_interp(mt, ct, multipoles)
            currents = interp
        return currents

    # --- private methods ---

    def __str__(self):
        """Str method."""
        str_h = [str(h) for h in self._harmonics]
        st = ''
        st += '# Magnet Excitation Data file' + '\n'
        st += '# ===========================' + '\n'
        st += '#' + '\n'
        st += '# label                      ' + self.label + '\n'
        st += '# harmonics                  ' + ' '.join(str_h) + '\n'
        st += '# main_multipole_harmonic    ' + \
            str(self._main_multipole_harmonic) + '\n'
        st += '# main_multipole_type        ' + \
            self._main_multipole_type + '\n'
        st += '# column_units               ' + 'A  '
        for h in self._harmonics:
            st += '{0:s} {1:s}  '.format(_util.get_multipole_si_units(h),
                                         _util.get_multipole_si_units(h))
        st += '\n'
        st += '\n'
        for i in range(len(self.currents)):
            st += '{0:>+9.3f}  '.format(self.currents[i])
            for h in self._harmonics:
                st += '{0:+.5e} {1:+.5e}  '.format(
                    self.multipoles['normal'][h][i],
                    self.multipoles['skew'][h][i])
            st += '\n'
        return st

    @staticmethod
    def _calc_interp(xt, yt, x):
        interp = _np.interp(x, xt, yt,
                            left=float('nan'), right=float('inf'))
        nan = _np.isnan(interp)
        inf = _np.isinf(interp)
        v = _util.linear_extrapolation(x[nan],
                                       xt[0], xt[1], yt[0], yt[1])
        interp[nan] = v
        v = _util.linear_extrapolation(x[inf],
                                       xt[-1], xt[-2], yt[-1], yt[-2])
        interp[inf] = v
        return interp

    def _read_text(self, text):

        self._init()
        lines = text.splitlines()
        self.currents = []

        for line in lines:
            line = line.strip()
            if not line:
                continue  # empty line
            if line[0] == '#':
                if len(line[1:].strip()) > 0:
                    token, *words = line[1:].split()
                    if token.lower() == 'label':
                        self.label = words[0]
                    if token.lower() == 'harmonics':
                        self._harmonics = [int(v) for v in words]
                    if token.lower() == 'main_harmonic':
                        self._main_multipole_harmonic = int(words[0])
                        self._main_multipole_type = words[1].lower()
                    if token.lower() == 'main_multipole_harmonic':
                        self._main_multipole_harmonic = int(words[0])
                    if token.lower() == 'main_multipole_type':
                        self._main_multipole_type = words[0]
                    if token.lower() == 'units':
                        self.column_units = ' '.join(words)
                    if token.lower() == 'column_units':
                        self.column_units = ' '.join(words)
            else:
                if not self.multipoles:
                    self.multipoles['normal'] = \
                        {h: [] for h in self._harmonics}
                    self.multipoles['skew'] = {h: [] for h in self._harmonics}
                cur, *exc = line.split()
                self.currents.append(float(cur))
                for j in range(len(self._harmonics)):
                    h = self._harmonics[j]
                    self.multipoles['normal'][h].append(float(exc[j*2+0]))
                    self.multipoles['skew'][h].append(float(exc[j*2+1]))
        # sort data
        idx = _np.argsort(self.currents)
        self.currents = [self.currents[idx[i]] for i in range(len(idx))]
        for h in self._harmonics:
            self.multipoles['normal'][h] = \
                [self.multipoles['normal'][h][idx[i]] for i in range(len(idx))]
            self.multipoles['skew'][h] = \
                [self.multipoles['skew'][h][idx[i]] for i in range(len(idx))]

        self._current_limits = (min(self.currents), max(self.currents))

    def _read_file(self, filename):

        with open(filename) as f:
            text = f.read()
        self._read_text(text)

    def _read_webs(self, label):

        self._fname = label
        text = _web.magnets_excitation_data_read(label)
        self._read_text(text)
