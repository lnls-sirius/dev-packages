
class PSWaveForm:

    @staticmethod
    def wfm_constant(nr_points, value=0.0):
        return tuple([value for i in range(nr_points)])

    @staticmethod
    def wfm_linear_ramp(nr_points, max_value=0.0):
        return tuple([max_value*i/(nr_points-1.0) for i in range(nr_points)])

    def __init__(self, data):
        self._data = tuple(data)

    @property
    def nr_points(self):
        return len(self._data)

    @property
    def data(self):
        return self._data
