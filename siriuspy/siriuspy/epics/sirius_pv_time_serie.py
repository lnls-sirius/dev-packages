from .sirius_pv import SiriusPV as _SiriusPV
import time as _time

class SiriusPVTimeSerie:

    def __init__(self, pv, time_window=None, nr_points = None, min_time_interval=0.0):

        self._pv = pv
        self._time_window = time_window
        self._min_time_interval = min_time_interval
        self._nr_points = nr_points

    @property
    def serie(self):
        """Return PV time series as two separate lists: timestamp and value"""
        self._update()
        raise NotImplemented # implementation here
        return timestamp_list, value_list

    def acquire():
        """Acquire a new time serie point data"""
        timestamp = _time.time()
        pv_timestamp, pv_value = self._pv.timestamp, self._pv.value
        if pv_timestamp >= timestamp - self._time_window:
            raise NotImplemented # implementation here
            return True # True:data point is acquired
        else:
            # this means that the whole series should be discarded
            raise NotImplemented # implementation here
            return False # False:data point is acquired

    def _update(self):
        """Update time serie according to current timestamp"""
        timestamp = _time.time()
        raise NotImplemented # implementation here

    def disconnect(self):
        self._pv.disconnect()

    def __str__(self):
        raise NotImplemented # implementation here
