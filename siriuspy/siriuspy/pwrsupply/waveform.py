# In ths future this class can implement an interface with the service that will
# store machine ramps and get data from it.

import numpy as _np
from siriuspy.csdevice.pwrsupply import default_wfmsize as _default_wfmsize
from siriuspy.csdevice.enumtypes import EnumTypes as _et
import os as _os


#_default_wfmsize = _et.enums('PSWfmLabelsTyp')


class PSWaveForm:

    path = '/tmp'

    @staticmethod
    def wfm_constant(label, nr_points=_default_wfmsize, value=0.0):
        return PSWaveForm(label, _np.array([value for i in range(nr_points)]))

    @staticmethod
    def wfm_linear_ramp(label, max_value=0.0):
        return PSWaveForm(label, _np.array([max_value*i/(_default_wfmsize-1.0) for i in range(_default_wfmsize)]))

    def __init__(self, label=None, data=None, filename=None):
        if filename is not None:
            self.load_from_file(filename)
        else:
            self._label = label
            self._data = _np.array(data)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def nr_points(self):
        return len(self._data)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = _np.array(value)

    def __getitem__(self, index):
        return self._data[index]

    def save_to_file(self, filename):

        with open(_os.path.join(PSWaveForm.path, filename), 'w') as fp:
            print(self._label, file=fp)
            for datum in self._data:
                print(str(datum), file=fp)

    def load_from_file(self, filename):
        with open(_os.path.join(PSWaveForm.path, filename)) as f:
            lines = [line.strip() for line in f]
        self._label = lines[0]
        self._data = _np.array([float(datum) for datum in lines[1:]])

    def __ne__(self, other):
        return self._label != other._label or (self._data != other._data).any()
