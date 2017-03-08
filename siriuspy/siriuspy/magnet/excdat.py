import numpy as _numpy
import siriuspy.macapp_web as _web
from . import util as _util

class ExcitationData:

    def __init__(self,filename_web=None, filename=None, text=None):

        self._init()

        if int(filename is not None)+ \
        int(text is not None)+ \
        int(filename_web is not None) > 1:
            raise Exception('ambiguous constructor arguments')

        if text:
            self.read_text(text)
        elif filename:
            self.read_file(filename)
        else:
            self.read_webs(filename_web)

    def _init(self):

        self.label = ''
        self.harmonics = []
        self.main_multipole_harmonic = None
        self.main_multipole_type = None
        self.column_units = ''
        self.currents = []
        self.multipoles = {}

    def read_text(self, text):

        self._init()
        lines = text.splitlines()
        self.currents = []

        for line in lines:
            line = line.strip()
            if not line: continue # empty line
            if line[0] == '#':
                if len(line[1:].strip())>0:
                    token, *words = line[1:].split()
                    if token.lower() == 'label': self.label = words[0]
                    if token.lower() == 'harmonics': self.harmonics = [int(v) for v in words]
                    if token.lower() == 'main_harmonic':
                        self.main_multipole_harmonic = int(words[0])
                        self.main_multipole_type = words[1].lower()
                    if token.lower() == 'main_multipole_harmonic': self.main_multipole_harmonic = int(words[0])
                    if token.lower() == 'main_multipole_type': self.main_multipole_type = words[0]
                    if token.lower() == 'units': self.column_units = ' '.join(words)
                    if token.lower() == 'column_units': self.column_units = ' '.join(words)
            else:
                if not self.multipoles:
                    self.multipoles['normal'] = {h:[] for h in self.harmonics}
                    self.multipoles['skew'] = {h:[] for h in self.harmonics}
                cur, *exc = line.split()
                self.currents.append(float(cur))
                for j in range(len(self.harmonics)):
                    h = self.harmonics[j]
                    self.multipoles['normal'][h].append(float(exc[j*2+0]))
                    self.multipoles['skew'][h].append(float(exc[j*2+1]))

        # sort data
        idx = _numpy.argsort(self.currents)
        self.currents = [self.currents[idx[i]] for i in range(len(idx))]
        for h in self.harmonics:
            self.multipoles['normal'][h] = [self.multipoles['normal'][h][idx[i]] for i in range(len(idx))]
            self.multipoles['skew'][h] = [self.multipoles['skew'][h][idx[i]] for i in range(len(idx))]

    def read_file(self, filename):

        with open(filename) as f:
            text = f.read()
        self.read_text(text)

    def read_webs(self, label):

        text = _web.magnets_excitation_data_read(label)
        self.read_text(text)

    def check_valid_curr(self, value):
        return self.currents[0] <= value <= self.currents[-1]

    def check_valid_mult(self, value, harmonic, multipole_type):
        multipoles = self.multipoles[multipole_type.lower()][harmonic]
        return min(multipoles) <= value <= max(multipoles)

    def interp_curr2mult(self, current, left='linear', right='linear'):
        """Interpolate multipoles for current values."""

        extrap_typ = 'interp'
        x = self.currents
        if current < x[0]:
            if isinstance(left,str):
                if left.lower() == 'linear':
                    extrap_typ = 'extrap_linear_left'
                elif left.lower() == 'exception':
                    raise Exception('current value is left-out of range')
                else:
                    raise Exception('invalid string value for "left" argument')
        elif current > x[-1]:
            if isinstance(right,str):
                if right.lower() == 'linear':
                    extrap_typ = 'extrap_linear_right'
                elif left.lower() == 'exception':
                    raise Exception('current value is right-out of range')
                else:
                    raise Exception('invalid string value for "right" argument')
        else:
            left = right = None

        multipoles = {'normal':{}, 'skew':{}}
        for h in self.harmonics:
            if extrap_typ == 'interp':
                if isinstance(left,str): left=None
                if isinstance(right,str): right=None
                y = self.multipoles['normal'][h]
                multipoles['normal'][h] = _numpy.interp(current, self.currents, y, left=left, right=right)
                y = self.multipoles['skew'][h]
                multipoles['skew'][h] = _numpy.interp(current, self.currents, y, left=left, right=right)
            elif extrap_typ == 'extrap_linear_left':
                y = self.multipoles['normal'][h]
                multipoles['normal'][h] = _utils.linear_extrapolation(current,x[0],x[1],y[0],y[1])
                y = self.multipoles['skew'][h]
                multipoles['skew'][h] = _utils.linear_extrapolation(current,x[0],x[1],y[0],y[1])
            elif extrap_typ == 'extrap_linear_right':
                y = self.multipoles['normal'][h]
                multipoles['normal'][h] = _utils.linear_extrapolation(current,x[-1],x[-2],y[-1],y[-2])
                y = self.multipoles['skew'][h]
                multipoles['skew'][h] = _utils.linear_extrapolation(current,x[-1],x[-2],y[-1],y[-2])
            else:
                pass # this point should never be reached

        return multipoles

    def interp_mult2curr(self, multipole, harmonic, multipole_type, left='linear', right='linear'):
        """Interpolate current from a specific multipole value."""

        multipoles = self.multipoles[multipole_type.lower()][harmonic]

        extrap_typ = 'interp'
        x = self.multipoles[multipole_type.lower()][harmonic]
        if multipole < min(x):
            if isinstance(left,str):
                if left.lower() == 'linear':
                    extrap_typ = 'extrap_linear_left'
                elif left.lower() == 'exception':
                    raise Exception('current value is left-out of range')
                else:
                    raise Exception('invalid string value for "left" argument')
        elif multipole > max(x):
            if isinstance(right,str):
                if right.lower() == 'linear':
                    extrap_typ = 'extrap_linear_right'
                elif left.lower() == 'exception':
                    raise Exception('current value is right-out of range')
                else:
                    raise Exception('invalid string value for "right" argument')
        else:
            left = right = None

        if extrap_typ == 'interp':
            if isinstance(left,str): left=None
            if isinstance(right,str): right=None
            if x[-1] < x[0]:
                current = _numpy.interp(multipole, x[::-1], self.currents[::-1], left=left, right=right)
            else:
                current = _numpy.interp(multipole, x, self.currents, left=left, right=right)
        elif extrap_typ == 'extrap_linear_left':
            current = ExcitationData._linear_extrapolation(multipole,x[0],x[1],self.currents[0],self.currents[1])
        elif extrap_typ == 'extrap_linear_right':
            current = ExcitationData._linear_extrapolation(multipole,x[-1],x[-2],self.currents[-1],self.currents[-2])
        else:
            pass # this should never be reached

        return current

    def set_multipoles(self, harmonic, multipoles_normal=None, multipoles_skew=None):
        """Set multipoles.

        Add new values if corresponding harmonic does not yet exist"""

        if not multipoles_normal:
            multipoles['normal'] = [0.0 for c in self.currents]
        elif len(multipole_normal) != len(self.currents):
            raise Exception('inconsistent number of current points in passed "multipoles_normal"')
        if not multipoles_skew:
            multipoles['skew'] = [0.0 for c in self.currents]
        elif len(multipole_skew) != len(self.currents):
            raise Exception('inconsistent number of current points in passed "multipoles_skew"')

        self.multipoles['normal'][harmonic] = multipoles_normal
        self.multipoles['skew'][harmonic] = multipoles_skew

    def __str__(self):
        tokens = ('label','harmonics', 'main_multipole_harmonic', 'main_multipole_type', 'units')
        fmt = '{0:<'+str(4+max([len(token) for token in tokens]))+'s}{1:s}\n'
        st = ''
        st += '# Magnet Excitation Data file' + '\n'
        st += '# ===========================' + '\n'
        st += '#' + '\n'
        st += '# label                      ' + self.label + '\n'
        st += '# harmonics                  ' + ' '.join([str(h) for h in self.harmonics]) + '\n'
        st += '# main_multipole_harmonic    ' + str(self.main_multipole_harmonic) + '\n'
        st += '# main_multipole_type        ' + self.main_multipole_type + '\n'
        st += '# column_units               ' + 'A  '
        for h in self.harmonics:
            st += '{0:s} {1:s}  '.format(_util.get_multipole_si_units(h), _util.get_multipole_si_units(h))
        st += '\n'
        st += '\n'
        for i in range(len(self.currents)):
            st += '{0:>+9.3f}  '.format(self.currents[i])
            for h in self.harmonics:
                st += '{0:+.5e} {1:+.5e}  '.format(self.multipoles['normal'][h][i],self.multipoles['skew'][h][i])
            st += '\n'
        return st
