# In ths future this class can implement an interface with the service that will
# store machine ramps and get data from it.

_default_nr_pts = 2000

class PSWaveForm:

    @staticmethod
    def wfm_constant(label, nr_points=_default_nr_pts, value=0.0):
        return PSWaveForm(label, list([value for i in range(nr_points)]))

    @staticmethod
    def wfm_linear_ramp(label, nr_points, period, max_value=0.0):
        return PSWaveForm(label, list([max_value*i/(nr_points-1.0) for i in range(nr_points)]))

    def __init__(self, label=None, data=None, filename=None):
        if filename is not None:
            self.load_from_file(filename)
        else:
            self._label = label
            self._data = list(data)

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
        self._data = [v for v in value]

    def __getitem__(self, index):
        return self._data[index]

    def save_to_file(self, filename):
        fp = open(filename, 'w')
        print(self._label, file=fp)
        for datum in self._data:
            print(str(datum), file=fp)

    def load_from_file(self, filename):
        with open(filename) as f:
            lines = [line.strip() for line in f]
        self._label = lines[0]
        self._data = [float(datum) for datum in lines[1:]]

    def __ne__(self, other):
        return self._label != other._label or self._data != other._data
