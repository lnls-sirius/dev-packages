# In ths future this class can implement an interface with the service that will
# store machine ramps and get data from it.


class PSWaveForm:

    @staticmethod
    def wfm_constant(nr_points, value=0.0):
        return PSWaveForm(0.0, tuple([value for i in range(nr_points)]))

    @staticmethod
    def wfm_linear_ramp(nr_points, period, max_value=0.0):
        return PSWaveForm(period, tuple([max_value*i/(nr_points-1.0) for i in range(nr_points)]))

    def __init__(self, period, data):
        self._period = period # [s]
        self._data = tuple(data)

    @property
    def nr_points(self):
        return len(self._data)

    @property
    def period(self):
        return self._period

    @property
    def data(self):
        return self._data

    def __getitem__(self, index):
        return self._data[index]
