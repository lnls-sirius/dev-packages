"""PV Arch Module."""

from .client import ClientArchiver as _ClientArchiver
from .time import Time as _Time


class PVDetails:
    """Archive PV Details."""

    _field2type = {
        'Number of elements': ('nelms', int),
        'Units:': ('units', str),
        'Host name': ('host_name', str),
        'Average bytes per event': ('avg_bytes_per_event', float),
        'Estimated storage rate (KB/hour)':
            ('estimated_storage_rate_kb_hour', float),
        'Estimated storage rate (MB/day)':
            ('estimated_storage_rate_mb_day', float),
        'Estimated storage rate (GB/year)':
            ('estimated_storage_rate_gb_year', float),
        }

    def __init__(self, pvname, connector=None):
        """."""
        self.pvname = pvname
        self.connector = connector
        self.is_scalar = None
        self.is_paused = None
        self.is_connected = None
        self.nelms = None
        self.units = None
        self.host_name = None
        self.avg_bytes_per_event = None
        self.estimated_storage_rate_kb_hour = None
        self.estimated_storage_rate_mb_day = None
        self.estimated_storage_rate_gb_year = None

    @property
    def connected(self):
        """."""
        if not self.connector:
            return False
        return self.connector.connected

    @property
    def request_url(self):
        """."""
        self.connect()
        url = self.connector.getPVDetails(self.pvname, get_request_url=True)
        return url

    @property
    def is_archived(self):
        """."""
        self.connect()
        data = self.connector.getPVDetails(self.pvname)
        if not data:
            return False
        return True

    def connect(self):
        """."""
        if self.connector is None:
            self.connector = _ClientArchiver()

    def update(self):
        """."""
        self.connect()
        data = self.connector.getPVDetails(self.pvname)
        if not data:
            return False
        for datum in data:
            # print(datum)
            field, value = datum['name'], datum['value']
            # value = value.replace(',', '.')
            value = value.replace(',', '')
            if field in PVDetails._field2type:
                fattr, ftype = PVDetails._field2type[field]
                if not value == 'Not enough info':
                    value = ftype(value)
                setattr(self, fattr, value)
            elif field == 'Is this a scalar:':
                self.is_scalar = (value.lower() == 'yes')
            elif field == 'Is this PV paused:':
                self.is_paused = (value.lower() == 'yes')
            elif field == 'Is this PV currently connected?':
                self.is_connected = (value.lower() == 'yes')
        return True

    def __str__(self):
        """."""
        rst = ''
        rst += '{:<30s}: {:}\n'.format('pvname', self.pvname)
        rst += '{:<30s}: {:}\n'.format('is_scalar', self.is_scalar)
        rst += '{:<30s}: {:}\n'.format('is_paused', self.is_paused)
        rst += '{:<30s}: {:}\n'.format('is_connected', self.is_connected)
        rst += '{:<30s}: {:}\n'.format('nelms', self.nelms)
        rst += '{:<30s}: {:}\n'.format('units', self.units)
        rst += '{:<30s}: {:}\n'.format('host_name', self.host_name)
        rst += '{:<30s}: {:}\n'.format(
            'avg_bytes_per_event', self.avg_bytes_per_event)
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_kb_hour',
            self.estimated_storage_rate_kb_hour)
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_mb_day',
            self.estimated_storage_rate_mb_day)
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_gb_year',
            self.estimated_storage_rate_gb_year)
        return rst


class PVData:
    """Archive PV Data."""

    def __init__(self, pvname, connector=None):
        """."""
        self._pvname = pvname
        self._connector = connector
        self._time_start = None
        self._time_stop = None
        self._timestamp = None
        self._value = None
        self._status = None
        self._severity = None
        self._parallel_query_bin_interval = 12*60*60  # 12h

    @property
    def pvname(self):
        """PVName."""
        return self._pvname

    @property
    def request_url(self):
        """Request url."""
        self.connect()
        url = self.connector.getData(
            self.pvname,
            self._time_start.get_iso8601(),
            self._time_stop.get_iso8601(),
            get_request_url=True)
        return url

    @property
    def is_archived(self):
        """Is archived."""
        self.connect()
        req = self.connector.getPVDetails(self.pvname)
        if not req.ok:
            return False
        return True

    def connect(self):
        """Connect."""
        if self.connector is None:
            self._connector = _ClientArchiver()

    @property
    def connector(self):
        """Connector."""
        return self._connector

    @property
    def connected(self):
        """Check connected."""
        return self.connector and self.connector.connected

    @property
    def timestamp_start(self):
        """Timestamp start."""
        if not self._time_start:
            return None
        return self._time_start.timestamp()

    @timestamp_start.setter
    def timestamp_start(self, new_timestamp):
        if not isinstance(new_timestamp, (float, int)):
            raise TypeError('expected argument of type float or int')
        self._time_start = _Time(timestamp=new_timestamp)

    @property
    def time_start(self):
        """Time start."""
        return self._time_start

    @time_start.setter
    def time_start(self, new_time):
        if not isinstance(new_time, _Time):
            raise TypeError('expected argument of type Time')
        self._time_start = new_time

    @property
    def timestamp_stop(self):
        """Timestamp stop."""
        if not self._time_stop:
            return None
        return self._time_stop.timestamp()

    @timestamp_stop.setter
    def timestamp_stop(self, new_timestamp):
        if not isinstance(new_timestamp, (float, int)):
            raise TypeError('expected argument of type float or int')
        self._time_stop = _Time(timestamp=new_timestamp)

    @property
    def time_stop(self):
        """Time stop."""
        return self._time_stop

    @time_stop.setter
    def time_stop(self, new_time):
        if not isinstance(new_time, _Time):
            raise TypeError('expected argument of type Time')
        self._time_stop = new_time

    @property
    def parallel_query_bin_interval(self):
        """Parallel query bin interval."""
        return self._parallel_query_bin_interval

    @parallel_query_bin_interval.setter
    def parallel_query_bin_interval(self, new_intvl):
        if not isinstance(new_intvl, (float, int)):
            raise TypeError('expected argument of type float or int')
        self._parallel_query_bin_interval = new_intvl

    @property
    def timestamp(self):
        """Timestamp data."""
        return self._timestamp

    @property
    def value(self):
        """Value data."""
        return self._value

    @property
    def status(self):
        """Status data."""
        return self._status

    @property
    def severity(self):
        """Severity data."""
        return self._severity

    def update(self, mean_sec=None):
        """Update."""
        self.connect()
        if None in (self.timestamp_start, self.timestamp_stop):
            print('Start and stop timestamps not defined! Aborting.')
            return
        process_type = 'mean' if mean_sec is not None else ''

        interval = self.parallel_query_bin_interval
        if self._time_start + interval >= self._time_stop:
            timestamp_start = self._time_start.get_iso8601()
            timestamp_stop = self._time_stop.get_iso8601()
        else:
            t_start = self._time_start
            t_stop = t_start + interval
            timestamp_start = [t_start.get_iso8601(), ]
            timestamp_stop = [t_stop.get_iso8601(), ]
            while t_stop < self._time_stop:
                t_start += interval
                t_stop = t_stop + interval
                if t_stop + interval > self._time_stop:
                    t_stop = self._time_stop
                timestamp_start.append(t_start.get_iso8601())
                timestamp_stop.append(t_stop.get_iso8601())

        data = self.connector.getData(
            self._pvname, timestamp_start, timestamp_stop,
            process_type=process_type, interval=mean_sec)
        if not data:
            return
        self._timestamp, self._value, self._status, self._severity = data
