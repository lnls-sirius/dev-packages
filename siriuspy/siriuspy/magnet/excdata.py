"""Excitation Data."""

import numpy as _np

from .. import clientweb as _web

from . import util as _util


class ExcitationData:
    """ExcitationData Class.

    This class implements access to excitation data paremeters and
    current - integrated field conversions.
    """

    def __init__(self, filename_web=None, filename=None, text=None):
        """Init method."""
        # define attributes
        self.label = None
        self._harmonics = None
        self._main_multipole_harmonic = None
        self._main_multipole_type = None
        self.rescaling_factor = None
        self.column_units = None
        self.currents = None
        self.multipoles = None

        # init attributes
        self._init()

        # check arguments
        args = (filename, text, filename_web)
        if sum((arg is not None for arg in args)) != 1:
            raise Exception('ambiguous constructor arguments')

        if text:
            self._read_text(text)
        elif filename:
            self._read_file(filename)
        else:
            self._read_webs(filename_web)

    def _init(self):

        self.label = ''
        self._harmonics = list()
        self._main_multipole_harmonic = None
        self._main_multipole_type = None
        self.rescaling_factor = 1.0
        self.column_units = ''
        self.currents = list()
        self.multipoles = dict()

    # --- properties ---

    @property
    def harmonics(self):
        """Return list with multipole harmonics."""
        return [harm for harm in self._harmonics]

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
        multipoles = self.multipoles[multipole_type][harmonic]
        return min(multipoles) <= value <= max(multipoles)

    def interp_curr2mult(self, currents, only_main_harmonic=False):
        """Interpolate multipoles for current values."""
        curr = self.currents
        multipoles = {'normal': {}, 'skew': {}}
        harmonics = (self.main_multipole_harmonic, ) if \
            only_main_harmonic else self.harmonics
        if _np.isscalar(currents):
            currents = _np.array([currents])
            for harm in harmonics:
                # normal component
                mpole = self.multipoles['normal'][harm]
                interp = _util.linear_interpolation(currents, curr, mpole)
                multipoles['normal'][harm] = interp[0]
                # skew component
                mpole = self.multipoles['skew'][harm]
                interp = _util.linear_interpolation(currents, curr, mpole)
                multipoles['skew'][harm] = interp[0]
        else:
            currents = _np.array(currents)
            for harm in harmonics:
                # normal component
                mpole = self.multipoles['normal'][harm]
                interp = _util.linear_interpolation(currents, curr, mpole)
                multipoles['normal'][harm] = interp
                # skew component
                mpole = self.multipoles['skew'][harm]
                interp = _util.linear_interpolation(currents, curr, mpole)
                multipoles['skew'][harm] = interp
        return multipoles

    def interp_mult2curr(self, multipoles, harmonic, multipole_type):
        """Interpolate current from a specific multipole value."""
        # sort correctly tabulated lists
        mpole = self.multipoles[multipole_type][harmonic]
        curr = self.currents
        if mpole[-1] <= mpole[0]:
            mpole, curr = mpole[::-1], self.currents[::-1]

        # do conversion
        if _np.isscalar(multipoles):
            multipoles = _np.array([multipoles])
            interp = _util.linear_interpolation(multipoles, mpole, curr)
            currents = interp[0]
        else:
            multipoles = _np.array(multipoles)
            interp = _util.linear_interpolation(multipoles, mpole, curr)
            currents = interp
        return currents

    # --- special methods ---

    def __str__(self):
        """Str method."""
        str_h = [str(harm) for harm in self._harmonics]
        rst = ''
        rst += '# Magnet Excitation Data file' + '\n'
        rst += '# ===========================' + '\n'
        rst += '#' + '\n'
        rst += '# label                      ' + self.label + '\n'
        rst += '# harmonics                  ' + ' '.join(str_h) + '\n'
        rst += '# main_multipole_harmonic    ' + \
            str(self._main_multipole_harmonic) + '\n'
        rst += '# main_multipole_type        ' + \
            self._main_multipole_type + '\n'
        rst += '# column_units               ' + 'A  '
        for harm in self._harmonics:
            rst += '{0:s} {1:s}  '.format(
                _util.get_multipole_si_units(harm),
                _util.get_multipole_si_units(harm))
        rst += '\n'
        rst += '\n'
        for i in range(len(self.currents)):
            rst += '{0:>+9.3f}  '.format(self.currents[i])
            for harm in self._harmonics:
                rst += '{0:+.5e} {1:+.5e}  '.format(
                    self.multipoles['normal'][harm][i],
                    self.multipoles['skew'][harm][i])
            rst += '\n'
        return rst

    # --- private methods ---

    def _process_comment_line(self, line):
        if line[1:].strip():
            token, *words = line[1:].split()
            if token.lower() == 'label':
                self.label = words[0]
            elif token.lower() == 'harmonics':
                self._harmonics = [int(vec) for vec in words]
            elif token.lower() == 'main_harmonic':
                self._main_multipole_harmonic = int(words[0])
                self._main_multipole_type = words[1].lower()
            elif token.lower() == 'main_multipole_harmonic':
                self._main_multipole_harmonic = int(words[0])
            elif token.lower() == 'main_multipole_type':
                self._main_multipole_type = words[0]
            elif token.lower() == 'units':
                self.column_units = ' '.join(words)
            elif token.lower() == 'column_units':
                self.column_units = ' '.join(words)
            elif token.lower() == 'rescaling_factor':
                self.rescaling_factor = float(words[0])

    def _process_data(self, line):
        if not self.multipoles:
            self.multipoles['normal'] = \
                {harm: [] for harm in self._harmonics}
            self.multipoles['skew'] = {harm: [] for harm in self._harmonics}
        cur, *exc = line.split()
        self.currents.append(float(cur))
        for j in range(len(self._harmonics)):
            harm = self._harmonics[j]
            nmpole = self.rescaling_factor * float(exc[j*2+0])
            smpole = self.rescaling_factor * float(exc[j*2+1])
            self.multipoles['normal'][harm].append(nmpole)
            self.multipoles['skew'][harm].append(smpole)

    def _read_text(self, text):
        self._init()
        lines = text.splitlines()
        self.currents = []

        for line in lines:
            line = line.strip()
            if not line:
                continue  # empty line
            if line[0] == '#':
                self._process_comment_line(line)
            else:
                self._process_data(line)

        # sort data
        idx = _np.argsort(self.currents)
        self.currents = [self.currents[idx[i]] for i in range(len(idx))]
        for harm in self._harmonics:
            self.multipoles['normal'][harm] = \
                [self.multipoles['normal'][harm][idx[i]]
                 for i in range(len(idx))]
            self.multipoles['skew'][harm] = \
                [self.multipoles['skew'][harm][idx[i]]
                 for i in range(len(idx))]
        self._current_limits = (min(self.currents), max(self.currents))

    def _read_file(self, filename):

        with open(filename) as f:
            text = f.read()
        self._read_text(text)

    def _read_webs(self, label):

        self._fname = label
        text = _web.magnets_excitation_data_read(label)
        self._read_text(text)
