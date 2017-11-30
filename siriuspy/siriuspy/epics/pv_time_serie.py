"""SiriusPVTimeSerie Class."""

import collections as _collections
import time as _time
import threading as _threading


class SiriusPVTimeSerie:
    """Class to handle time series from pv monitoring."""

    def __init__(self, pv,
                 time_window=None,
                 nr_max_points=None,
                 time_min_interval=0.0,
                 mode=0):
        """Class constructor."""
        self._pv = pv
        self._time_window = time_window
        self._time_min_interval = time_min_interval
        self._nr_max_points = nr_max_points
        self._timestamp_deque = _collections.deque(maxlen=self._nr_max_points)
        self._value_deque = _collections.deque(maxlen=self._nr_max_points)
        self._mode = mode
        if self._mode == 1:
            self._th_auto_acquire = _threading.Thread(
                target=self._auto_acquire, daemon=True)
            self._stop_auto_acquire = False
            self._th_auto_acquire.start()
        else:
            self._stop_auto_acquire = True

    @property
    def time_window(self):
        """Time window of datapoints."""
        return self._time_window

    @time_window.setter
    def time_window(self, value):
        self._time_window = value
        timestamp = _time.time()
        self._update(timestamp)

    @property
    def time_min_interval(self):
        """Minimum time interval between the datapoints."""
        return self._time_min_interval

    @time_min_interval.setter
    def time_min_interval(self, value):
        self._time_min_interval = value

        if len(self._timestamp_deque) > 0:
            old_timestamp_deque = _collections.deque(
                self._timestamp_deque, maxlen=self._nr_max_points)
            old_value_deque = _collections.deque(
                self._value_deque, maxlen=self._nr_max_points)
            self._timestamp_deque = _collections.deque(
                maxlen=self._nr_max_points)
            self._value_deque = _collections.deque(
                maxlen=self._nr_max_points)

            aux = old_timestamp_deque.pop()
            self._timestamp_deque.appendleft(aux)
            aux = old_value_deque.pop()
            self._value_deque.appendleft(aux)

            while len(old_timestamp_deque) > 0:
                if self._time_min_interval < (
                        self._timestamp_deque[0] - old_timestamp_deque[-1]):
                    aux = old_timestamp_deque.pop()
                    self._timestamp_deque.appendleft(aux)
                    aux = old_value_deque.pop()
                    self._value_deque.appendleft(aux)
                else:
                    old_timestamp_deque.pop()
                    old_value_deque.pop()

    @property
    def nr_max_points(self):
        """Maximum number of datapoints."""
        return self._nr_max_points

    @nr_max_points.setter
    def nr_max_points(self, value):
        self._nr_max_points = value
        self._timestamp_deque = _collections.deque(
            self._timestamp_deque, maxlen=self._nr_max_points)
        self._value_deque = _collections.deque(
            self._value_deque, maxlen=self._nr_max_points)

    @property
    def mode(self):
        """Mode of acquisition: 0 if manual and 1 if automatic."""
        return self._mode

    @mode.setter
    def mode(self, value):
        if self._mode != value:
            self._mode = value
            if self._mode == 1:
                self._th_auto_acquire = _threading.Thread(
                    target=self._auto_acquire, daemon=True)
                self._stop_auto_acquire = False
                self._th_auto_acquire.start()
            else:
                self._stop_auto_acquire = True

    @property
    def serie(self):
        """PV time series, as two separate lists: timestamp and value."""
        timestamp = _time.time()
        self._update(timestamp)
        timestamp_list = [item-timestamp for item in self._timestamp_deque]
        value_list = [item for item in self._value_deque]
        return timestamp_list, value_list

    def acquire(self):
        """Acquire a new time serie datapoint.

        Returns True if datapoint was acquired and False otherwise.
        """
        # check if pv is connected
        if self.connected():
            timestamp = _time.time()
            pv_timestamp, pv_value = self._pv.timestamp, self._pv.value

            # check if it is a new datapoint
            if len(self._timestamp_deque) == 0 or \
                    pv_timestamp != self._timestamp_deque[-1]:
                # check if there is a limiting time_window
                if self._time_window is None:
                    # check if there is a limiting time_min_interval
                    if len(self._timestamp_deque) == 0 or \
                            self._time_min_interval <= \
                            timestamp-self._timestamp_deque[-1]:
                        self._timestamp_deque.append(pv_timestamp), \
                            self._value_deque.append(pv_value)
                        return True
                    else:
                        # print('not acquired: time interval not sufficient')
                        return False
                else:
                    # Check if the datapoints in the deques are yet valid
                    # to the limiting time_window
                    self._update(timestamp)
                    # check if the new point is within the limiting time_window
                    if pv_timestamp >= timestamp - self._time_window:
                        if len(self._timestamp_deque) == 0 or \
                                self._time_min_interval <= \
                                timestamp-self._timestamp_deque[-1]:
                            self._timestamp_deque.append(pv_timestamp), \
                                self._value_deque.append(pv_value)
                            return True
                        else:
                            # print('not acquired: not enough time interval')
                            return False
                    else:
                        # print('not acquired: not within time_window')
                        return False
            else:
                # print('not acquired: item already in deque')
                return False
        else:
            # print('not acquired: pv not connected')
            return False

    def _auto_acquire(self):
        while not self._stop_auto_acquire:
            self.acquire()
            _time.sleep(self.time_min_interval)

    def _update(self, timestamp):
        """Update time serie according to current timestamp."""
        if len(self._timestamp_deque) > 0:
            if self._timestamp_deque[-1] <= timestamp - self._time_window:
                self.clearserie()

            elif self._timestamp_deque[0] >= timestamp - self._time_window:
                pass

            else:
                low_interval_end = 0
                high_interval_end = len(self._timestamp_deque)-1
                search_index = (high_interval_end - low_interval_end)//2

                while low_interval_end != search_index:
                    if self._timestamp_deque[search_index] <= \
                            timestamp - self._time_window:
                        low_interval_end = search_index
                        search_index = ((
                            high_interval_end - low_interval_end)//2 +
                            low_interval_end)
                    else:
                        high_interval_end = search_index
                        search_index = ((
                            high_interval_end - low_interval_end)//2 +
                            low_interval_end)

                for item in range(search_index + 1):
                    self._timestamp_deque.popleft(), \
                        self._value_deque.popleft()

    def clearserie(self):
        """Clear time serie."""
        self._timestamp_deque.clear()
        self._value_deque.clear()

    def connected(self):
        """Check PV connection."""
        return self._pv.connected

    def __str__(self):
        """String representation of time series."""
        raise NotImplemented
