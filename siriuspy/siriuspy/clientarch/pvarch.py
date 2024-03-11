"""PV Arch Module."""

from copy import deepcopy as _dcopy

import numpy as _np

from mathphys.functions import save_pickle as _save_pickle, \
    load_pickle as _load_pickle

from . import exceptions as _exceptions
from .client import ClientArchiver as _ClientArchiver
from .time import Time as _Time, get_time_intervals as _get_time_intervals


class _Base:

    def __init__(self, connector=None):
        self._connector = None
        self.connector = connector
        self.connect()

    @property
    def is_archived(self):
        """Is archived."""
        self.connect()
        return self.connector.getPVDetails(self.pvname) is not None

    def connect(self):
        """Connect."""
        if self.connector is None:
            self._connector = _ClientArchiver()

    @property
    def connector(self):
        """Connector."""
        return self._connector

    @connector.setter
    def connector(self, conn):
        if conn is None:
            return
        elif isinstance(conn, _ClientArchiver):
            self._connector = conn
        elif isinstance(conn, str):
            self._connector = _ClientArchiver(server_url=conn)
        else:
            raise TypeError(
                'Variable conn must be a str or ClientArchiver object.')

    @property
    def timeout(self):
        """Connection timeout."""
        return self.connector.timeout

    @timeout.setter
    def timeout(self, value):
        """Set connection timeout."""
        self.connector.timeout = float(value)

    @property
    def connected(self):
        """."""
        if not self.connector:
            return False
        return self.connector.connected


class PVDetails(_Base):
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
        super().__init__(connector)
        self.pvname = pvname
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

    def update(self, timeout=None):
        """."""
        self.connect()
        if timeout is not None:
            self.timeout = timeout
        data = self.connector.getPVDetails(self.pvname)
        if not data:
            return False
        for datum in data:
            # print(datum)
            field, value = datum['name'], datum['value']
            if value is None:
                continue
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


class PVData(_Base):
    """Archive PV Data."""

    def __init__(self, pvname, connector=None):
        """Initialize."""
        super().__init__(connector)
        self._pvname = pvname
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
    def timestamp_start(self):
        """Timestamp start."""
        if not self._time_start:
            return None
        return self._time_start.timestamp()

    @timestamp_start.setter
    def timestamp_start(self, new_timestamp):
        if not isinstance(new_timestamp, (float, int)):
            raise _exceptions.TypeError(
                'expected argument of type float or int, got ' +
                str(type(new_timestamp)))
        self._time_start = _Time(timestamp=new_timestamp)

    @property
    def time_start(self):
        """Time start."""
        return self._time_start

    @time_start.setter
    def time_start(self, new_time):
        if not isinstance(new_time, _Time):
            raise _exceptions.TypeError(
                'expected argument of type Time, got '+str(type(new_time)))
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
            raise _exceptions.TypeError(
                'expected argument of type float or int, got ' +
                str(type(new_timestamp)))
        self._time_stop = _Time(timestamp=new_timestamp)

    @property
    def time_stop(self):
        """Time stop."""
        return self._time_stop

    @time_stop.setter
    def time_stop(self, new_time):
        if not isinstance(new_time, _Time):
            raise _exceptions.TypeError(
                'expected argument of type Time, got ' + str(type(new_time)))
        self._time_stop = new_time

    @property
    def parallel_query_bin_interval(self):
        """Parallel query bin interval."""
        return self._parallel_query_bin_interval

    @parallel_query_bin_interval.setter
    def parallel_query_bin_interval(self, new_intvl):
        if not isinstance(new_intvl, (float, int)):
            raise _exceptions.TypeError(
                'expected argument of type float or int, got ' +
                str(type(new_intvl)))
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

    def update(self, mean_sec=None, parallel=True, timeout=None):
        """Update."""
        self.connect()
        if timeout is not None:
            self.timeout = timeout
        if None in (self.timestamp_start, self.timestamp_stop):
            print('Start and stop timestamps not defined! Aborting.')
            return
        process_type = 'mean' if mean_sec is not None else ''

        interval = self.parallel_query_bin_interval
        if parallel:
            timestamp_start, timestamp_stop = _get_time_intervals(
                self._time_start, self._time_stop, interval,
                return_isoformat=True)
        else:
            timestamp_start = self._time_start.get_iso8601()
            timestamp_stop = self._time_stop.get_iso8601()

        data = self.connector.getData(
            self._pvname, timestamp_start, timestamp_stop,
            process_type=process_type, interval=mean_sec)
        if not data:
            return
        self.set_data(**data)

    def set_data(self, timestamp, value, status, severity):
        """Auxiliary method to set data. Used by PVDataSet."""
        self._timestamp = self._value = self._status = self._severity = None
        if timestamp is not None:
            self._timestamp = _np.asarray(timestamp)
            self._value = _np.asarray(value)
            self._status = _np.asarray(status)
            self._severity = _np.asarray(severity)

    def to_dict(self):
        """Return dictionary with PV properties.

        Returns:
            dict: dictionary with fields:
                server_url (str): url of the Archiver server.
                pvname (str): the name of the PV.
                timestamp_start (time.time): start of acquisition time.
                timestamp_stop (time.time): end of acquisition time.
                data (dict): dictionary with archiver data  with fields:
                    value (numpy.ndarray): values of the PV.
                    timestamp (numpy.ndarray): timestamps of the PV.
                    status (numpy.ndarray): status of the PV.
                    severity (numpy.ndarray): severity of the PV.

        """
        return dict(
            server_url=self.connector.server_url,
            pvname=self.pvname,
            timestamp_start=self.timestamp_start,
            timestamp_stop=self.timestamp_stop,
            data=dict(
                timestamp=self.timestamp, value=self.value,
                status=self.status, severity=self.severity)
            )

    @staticmethod
    def from_dict(infos):
        """Return PVData object with information in data.

        Args:
            infos (dict): must have the same fields as the dictionary returned
                by PVData.to_dict method.

        Returns:
            PVData: with values compatible with data.

        """
        pvdata = PVData(infos['pvname'], connector=infos['server_url'])
        pvdata.timestamp_start = infos['timestamp_start']
        pvdata.timestamp_stop = infos['timestamp_stop']
        pvdata.set_data(**infos['data'])
        return pvdata

    def to_pickle(self, fname, overwrite=False):
        """Create pickle file with complete PVData.

        The data saved is the dictionary returned by PVData.to_dict method.

        Args:
            fname (str): name of the file to save.
            overwrite (bool, optional): Whether to overwrite existing file
                with same name or not. Defaults to False.

        """
        _save_pickle(self.to_dict(), fname, overwrite=overwrite)

    @staticmethod
    def from_pickle(fname):
        """Load data from pickle file and return PVData object.

        Args:
            fname (str): name of the file to load.

        Returns:
            PVData: with values from the pickle file.

        """
        return PVData.from_dict(_load_pickle(fname))


class PVDataSet(_Base):
    """A set of PVData objects."""

    def __init__(self, pvnames, connector=None):
        """Initialize."""
        super().__init__(connector)
        self._pvnames = pvnames
        self._time_start = None
        self._time_stop = None
        self._parallel_query_bin_interval = 12*60*60  # 12h
        self._pvdata = self._init_pvdatas(pvnames, self.connector)

    @property
    def pvnames(self):
        """PV names."""
        return _dcopy(self._pvnames)

    @pvnames.setter
    def pvnames(self, new_pvnames):
        self._pvnames = new_pvnames
        self._pvdata = self._init_pvdatas(new_pvnames, self.connector)

    @property
    def is_archived(self):
        """Is archived."""
        self.connect()
        for pvn in self._pvnames:
            if self.connector.getPVDetails(pvn) is None:
                return False
        return True

    @property
    def timestamp_start(self):
        """Timestamp start."""
        if not self._time_start:
            return None
        return self._time_start.timestamp()

    @timestamp_start.setter
    def timestamp_start(self, new_timestamp):
        if not isinstance(new_timestamp, (float, int)):
            raise _exceptions.TypeError(
                'expected argument of type float or int, got ' +
                str(type(new_timestamp)))
        self._time_start = _Time(timestamp=new_timestamp)
        for pvname in self._pvnames:
            self._pvdata[pvname].time_start = self._time_start

    @property
    def time_start(self):
        """Time start."""
        return self._time_start

    @time_start.setter
    def time_start(self, new_time):
        if not isinstance(new_time, _Time):
            raise _exceptions.TypeError(
                'expected argument of type Time, got '+str(type(new_time)))
        self._time_start = new_time
        for pvname in self._pvnames:
            self._pvdata[pvname].time_start = self._time_start

    @property
    def timestamp_stop(self):
        """Timestamp stop."""
        if not self._time_stop:
            return None
        return self._time_stop.timestamp()

    @timestamp_stop.setter
    def timestamp_stop(self, new_timestamp):
        if not isinstance(new_timestamp, (float, int)):
            raise _exceptions.TypeError(
                'expected argument of type float or int, got ' +
                str(type(new_timestamp)))
        self._time_stop = _Time(timestamp=new_timestamp)
        for pvname in self._pvnames:
            self._pvdata[pvname].time_stop = self._time_stop

    @property
    def time_stop(self):
        """Time stop."""
        return self._time_stop

    @time_stop.setter
    def time_stop(self, new_time):
        if not isinstance(new_time, _Time):
            raise _exceptions.TypeError(
                'expected argument of type Time, got '+str(type(new_time)))
        self._time_stop = new_time
        for pvname in self._pvnames:
            self._pvdata[pvname].time_stop = self._time_stop

    @property
    def parallel_query_bin_interval(self):
        """Parallel query bin interval."""
        return self._parallel_query_bin_interval

    @parallel_query_bin_interval.setter
    def parallel_query_bin_interval(self, new_intvl):
        if not isinstance(new_intvl, (float, int)):
            raise _exceptions.TypeError(
                'expected argument of type float or int, got ' +
                str(type(new_intvl)))
        self._parallel_query_bin_interval = new_intvl
        for pvname in self._pvnames:
            self._pvdata[pvname].parallel_query_bin_interval = \
                self._parallel_query_bin_interval

    def update(self, mean_sec=None, parallel=True, timeout=None):
        """Update."""
        self.connect()
        if timeout is not None:
            self.timeout = None
        if None in (self.timestamp_start, self.timestamp_stop):
            print('Start and stop timestamps not defined! Aborting.')
            return
        process_type = 'mean' if mean_sec is not None else ''

        interval = self.parallel_query_bin_interval
        if parallel:
            timestamp_start, timestamp_stop = _get_time_intervals(
                self._time_start, self._time_stop, interval,
                return_isoformat=True)
        else:
            timestamp_start = self._time_start.get_iso8601()
            timestamp_stop = self._time_stop.get_iso8601()

        data = self.connector.getData(
            self._pvnames, timestamp_start, timestamp_stop,
            process_type=process_type, interval=mean_sec)

        if not data:
            return
        if len(self._pvnames) == 1:
            pvname = self._pvnames[0]
            data = {pvname: data}
        for pvname in self._pvnames:
            self._pvdata[pvname].set_data(**data[pvname])

    def _init_pvdatas(self, pvnames, connector):
        pvdata = dict()
        for pvname in pvnames:
            pvdata[pvname] = PVData(pvname, connector)
            pvdata[pvname].parallel_query_bin_interval = \
                self._parallel_query_bin_interval
            if self._time_start is not None:
                pvdata[pvname].time_start = self._time_start
            if self._time_stop is not None:
                pvdata[pvname].time_stop = self._time_stop
        return pvdata

    def __getitem__(self, val):
        """Get item."""
        if isinstance(val, str):
            return self._pvdata[val]
        elif isinstance(val, int):
            return self._pvdata[self._pvnames[val]]
        else:
            raise TypeError('Item must be int or str.')

    def __iter__(self):
        """Iterate over object."""
        for pvn in self.pvnames:
            yield self[pvn]

    def __len__(self):
        """Size of the object."""
        return len(self.pvnames)

    def to_dict(self):
        """Return dictionary with PV properties.

        Returns:
            dict: dictionary with fields:
                server_url (str): url of the Archiver server.
                pvnames (list): the names of the PVs.
                timestamp_start (time.time): start of acquisition time.
                timestamp_stop (time.time): end of acquisition time.
                pvdata_info (list): with dictionaries containing the data for
                    all PVs. Compatible input for PVData.from_dict.

        """
        data = dict(
            server_url=self.connector.server_url,
            pvnames=self.pvnames,
            timestamp_start=self.timestamp_start,
            timestamp_stop=self.timestamp_stop)
        data['pvdata_info'] = [self[pvn].to_dict() for pvn in self._pvnames]
        return data

    @staticmethod
    def from_dict(info):
        """Return PVDataSet object with information in data.

        Args:
            info (dict): must have the same fields as the dictionary returned
                by PVDataSet.to_dict method.

        Returns:
            PVDataSet: with values compatible with data.

        """
        pvdataset = PVDataSet(info['pvnames'], info['server_url'])
        pvdataset.timestamp_start = info['timestamp_start']
        pvdataset.timestamp_stop = info['timestamp_stop']
        for i, pvdata in enumerate(pvdataset):
            pvdata.set_data(**info['pvdata_info'][i]['data'])
        return pvdataset

    def to_pickle(self, fname, overwrite=False):
        """Create pickle file with complete PVDataSet.

        The data saved is the dictionary returned by PVDataSet.to_dict method.

        Args:
            fname (str): name of the file to save.
            overwrite (bool, optional): Whether to overwrite existing file
                with same name or not. Defaults to False.

        """
        _save_pickle(self.to_dict(), fname, overwrite=overwrite)

    @staticmethod
    def from_pickle(fname):
        """Load data from pickle file and return PVDataSet object.

        Args:
            fname (str): name of the file to load.

        Returns:
            PVDataSet: with values from the pickle file.

        """
        return PVDataSet.from_dict(_load_pickle(fname))
