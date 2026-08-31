"""PV Arch Module."""

from copy import deepcopy as _dcopy

import numpy as _np
from mathphys.functions import (
    load_pickle as _load_pickle,
    save_pickle as _save_pickle
)

from .. import envars as _envars
from . import exceptions as _exceptions
from .client import ClientArchiver as _ClientArchiver
from .time import Time as _Time


class _Base:
    def __init__(self, connector=None, beamline_data=False):
        self._connector = None
        self.connector = connector
        self.connect(beamline_data=beamline_data)

    @property
    def is_archived(self):
        """Is archived."""
        self.connect()
        return self.connector.get_pv_details(self.pvname) is not None

    def connect(self, beamline_data=False):
        """Connect."""
        if self.connector is None:
            url_beamline = _envars.SRVURL_ARCHIVER_BEAMLINE_DATA
            url_machine = _envars.SRVURL_ARCHIVER
            url = url_beamline if beamline_data else url_machine
            self._connector = _ClientArchiver(server_url=url)

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
                'Variable conn must be a str or ClientArchiver object.'
            )

    @property
    def is_beamline_data(self):
        """Whether server url points to machine or beamline data.

        Return None in case the url is not recognized as either machine or
        beamline.
        """
        if self._connector.server_url == _envars.SRVURL_ARCHIVER_BEAMLINE_DATA:
            return True
        elif self._connector.server_url == _envars.SRVURL_ARCHIVER:
            return False
        else:
            return None

    @property
    def query_timeout(self):
        """Request timeout for each query.

        This is a global setting for the connector, so all PVData objects
        share it, but we allow it to be set through PVDataSet for convenience.

        """
        return self.connector.query_timeout

    @query_timeout.setter
    def query_timeout(self, value):
        """Set request timeout for each query."""
        self.connector.query_timeout = float(value)

    @property
    def connected(self):
        """."""
        if not self.connector:
            return False
        return self.connector.connected

    def switch_to_machine_data(self):
        """."""
        if self.connector:
            self.connector.switch_to_machine_data()

    def switch_to_beamline_data(self):
        """."""
        if self.connector:
            self.connector.switch_to_beamline_data()

    def gen_archviewer_url_link(
        self,
        pvnames,
        time_start,
        time_stop,
        time_ref=None,
        pvoptnrpts=None,
        pvcolors=None,
        pvusediff=False,
    ):
        """Generate a Archiver Viewer URL for the given PVs.

        Parameters
        ----------
        pvnames : iterable[str]
            Iterable of PV names to include in the viewer.
        time_start : datetime.datetime or siriuspy.clientarch.time.Time,
            optional Start time of the interval to display.
        time_stop : datetime.datetime or siriuspy.clientarch.time.Time,
            optional Stop time of the interval to display.
        time_ref : datetime.datetime or siriuspy.clientarch.time.Time, optional
            reference time used when enabling the diff view.
        pvoptnrpts : iterable[int], optional
            Iterable with optimization point counts for each PV (0 or None
            means no optimization). Must have the same length as `pvnames`.
            Defaults to None.
        pvcolors : iterable[str or None], optional
            Iterable with hex color strings (e.g. "#00ff00") or None for
            each PV. Must have the same length as `pvnames`. Defaults to None.
        pvusediff : iterable[bool], optional
            Iterable indicating whether to enable the diff option for each PV.
            Must have the same length as `pvnames`. Defaults to False.

        Returns
        -------
        str
            A full Archiver Viewer URL containing the compressed PV
            configuration.
        """
        url = _ClientArchiver.gen_archviewer_url_link(
            pvnames=pvnames,
            time_start=time_start,
            time_stop=time_stop,
            time_ref=time_ref,
            pvoptnrpts=pvoptnrpts,
            pvcolors=pvcolors,
            pvusediff=pvusediff,
        )
        return url


class PVDetails(_Base):
    """Archive PV Details."""

    _field2type = {
        'Number of elements': ('nelms', int),
        'Units:': ('units', str),
        'Host name': ('host_name', str),
        'Average bytes per event': ('avg_bytes_per_event', float),
        'Estimated storage rate (KB/hour)': (
            'estimated_storage_rate_kb_hour',
            float,
        ),
        'Estimated storage rate (MB/day)': (
            'estimated_storage_rate_mb_day',
            float,
        ),
        'Estimated storage rate (GB/year)': (
            'estimated_storage_rate_gb_year',
            float,
        ),
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
        url = self.connector.get_pv_details(self.pvname, get_request_url=True)
        return url

    def update(self, query_timeout=None):  # noqa: C901
        """."""
        self.connect()

        if query_timeout is not None:
            query_timeout0 = self.query_timeout
            self.query_timeout = query_timeout

        try:
            data = self.connector.get_pv_details(self.pvname)
        finally:
            if query_timeout is not None:
                self.query_timeout = query_timeout0

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
                self.is_scalar = value.lower() == 'yes'
            elif field == 'Is this PV paused:':
                self.is_paused = value.lower() == 'yes'
            elif field == 'Is this PV currently connected?':
                self.is_connected = value.lower() == 'yes'

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
            'avg_bytes_per_event', self.avg_bytes_per_event
        )
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_kb_hour',
            self.estimated_storage_rate_kb_hour,
        )
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_mb_day', self.estimated_storage_rate_mb_day
        )
        rst += '{:<30s}: {:}\n'.format(
            'estimated_storage_rate_gb_year',
            self.estimated_storage_rate_gb_year,
        )
        return rst


class PVData(_Base):
    """Archive PV Data."""

    ProcessingTypes = _ClientArchiver.ProcessingTypes

    def __init__(self, pvname, connector=None, beamline_data=False):
        """Initialize."""
        super().__init__(connector, beamline_data=beamline_data)
        self._pvname = pvname
        self._timestamp = None
        self._value = None
        self._status = None
        self._severity = None
        self._time_start = _Time.now()
        self._time_stop = self._time_start
        self._query_split_interval = self.connector.query_split_interval
        self._processing_type = self.ProcessingTypes.None_
        self._processing_type_param1 = None
        self._processing_type_param2 = 3.0  # number of sigma

    def __str__(self):
        """."""
        stg = ''
        stg += 'Connector Properties:\n'
        stg += '    {:<30s}: {:d}\n'.format(
            'query_max_concurrency: ', self.query_max_concurrency
        )
        stg += '    {:<30s}: {:.1f}\n'.format(
            'query_timeout [s]', self.query_timeout
        )
        stg += '\nPV Data Properties:\n'

        tss = self.time_start.get_iso8601()
        tsp = self.time_stop.get_iso8601()
        stg += '    {:<30s}: {:}\n'.format('pvname', self.pvname)
        stg += '    {:<30s}: {:}\n'.format('time_start', tss)
        stg += '    {:<30s}: {:}\n'.format('time_stop', tsp)
        stg += '    {:<30s}: {:d}\n'.format(
            'query_split_interval [s]', self.query_split_interval
        )
        prty = self.processing_type
        pr1 = self.processing_type_param1
        stg += '    {:<30s}: {:}\n'.format(
            'processing_type', prty if prty else "''"
        )
        if prty == self.ProcessingTypes.SelectByChange:
            pr1 = 'None' if pr1 is None else f'{pr1:.2g}'
            stg += '    {:<30s}: {:}\n'.format(
                'processing_type_param1 [val. units]', pr1
            )
        elif prty != self.ProcessingTypes.None_:
            pr1 = 'None' if pr1 is None else f'{pr1:d}'
            stg += '    {:<30s}: {:}\n'.format(
                'processing_type_param1 [s]', pr1
            )
        if prty in (
            self.ProcessingTypes.Outliers,
            self.ProcessingTypes.IgnoreOutliers,
        ):
            stg += '    {:<30s}: {:.2g}\n'.format(
                'processing_type_param2 [std/mean]',
                self.processing_type_param2,
            )

        stg += '    {:<30s}'.format('Data Length: ')
        if self.timestamp is not None:
            stg += '{:d}\n'.format(len(self.timestamp))
        else:
            stg += 'Not loaded yet.\n'
        return stg

    # -------- PV data properties --------

    @property
    def pvname(self):
        """PVName."""
        return self._pvname

    @property
    def request_url(self):
        """Request url."""
        self.connect()
        return self.connector.get_request_url_for_get_data(
            self._pvname,
            self.time_start,
            self.time_stop,
            query_split_interval=self.query_split_interval,
            proc_type=self.processing_type,
            proc_type_param1=self.processing_type_param1,
            proc_type_param2=self.processing_type_param2,
        )

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

    # ------- PV data acquisition and processing properties --------

    @property
    def query_split_interval(self):
        """Queries larger than this interval will be split.

        If set to 0 or None, no splitting will be done.
        """
        return self._query_split_interval

    @query_split_interval.setter
    def query_split_interval(self, new_intvl):
        if new_intvl is None:
            new_intvl = 0
        if not isinstance(new_intvl, (float, int)):
            raise _exceptions.TypeError(
                'expected argument of type float or int, got '
                + str(type(new_intvl))
            )
        self._query_split_interval = max(int(new_intvl), 0)

    @property
    def query_max_concurrency(self):
        """Query max concurrency.

        This is a global setting for the connector, so all PVData objects
        share it, but we allow it to be set through PVDataSet for convenience.

        """
        return self.connector.query_max_concurrency

    @query_max_concurrency.setter
    def query_max_concurrency(self, new_intvl):
        self.connector.query_max_concurrency = new_intvl

    @property
    def time_start(self):
        """Time start.

        Return siriuspy.clientarch.time.Time object.
        """
        return self._time_start

    @time_start.setter
    def time_start(self, new_time):
        """Accept any value that can be converted to a Time object."""
        self._time_start = _Time(new_time)

    @property
    def time_stop(self):
        """Time stop.

        Return siriuspy.clientarch.time.Time object.
        """
        return self._time_stop

    @time_stop.setter
    def time_stop(self, new_time):
        """Accept any value that can be converted to a Time object."""
        self._time_stop = _Time(new_time)

    @property
    def processing_type(self):
        """Data processing type to use for query.

        For details on each operator, please, refer to the section
        Processing of data of the following page:
        https://epicsarchiver.readthedocs.io/en/latest/user/userguide.html

        The options implemented here are:

        The options below do not take any aditional parameter:
            '' --> No processing, raw data is returned.
            'ncount' --> total number of updates in the whole interval.

        All types of processing below, require an aditional parameter,
        controlled by the input `processing_type_param1`. Then the
        refered statistics will be performed within this interval:
            'mean'
            'median'
            'std'
            'variance'
            'popvariance' --> population variance.
            'kurtosis'
            'skewness'
            'mini' --> same as min, which is also accepted by the archiver.
            'maxi' --> same as max, which is also accepted by the archiver.
            'jitter' --> std / mean for each bin.
            'count' --> number of updates in each bin.
            'firstSample'
            'lastSample'
            'firstFill' --> see url for difference to `'firstSample'`.
            'lastFill' --> see url for difference to `'lastSample'`.
            'linear' --> not sure, look at the archiver docs.
            'loess' --> not sure, look at the archiver docs.

        The processing below also use an aditional parameter, but its
        meaning is different from the statistics above:
            'optimized' --> the parameter means the total number of points
                            to be returned, instead of the time interval.
            'optimLastSample' --> close to 'opimized'. See docs for diff.
            'nth' --> return every nth sample.
            'deadBand' --> similar to ADEL. Only return when values change
                by a certain amount.

        For both statistics below a second parameter is needed to configure
        acquisition, controlled by `processing_type_param2`. This
        parameter controls the number of standard deviations to consider
        in the filtering bellow. The default of this parameter is 3.0:
            'ignoreflyers' --> whether to ignore outliers
            'flyers' --> only return outliers
        """
        return self._processing_type

    @processing_type.setter
    def processing_type(self, new_type):
        if not isinstance(new_type, str):
            raise _exceptions.TypeError(
                'expected argument of type str, got ' + str(type(new_type))
            )
        elif new_type not in self.ProcessingTypes:
            raise _exceptions.ValueError(
                f'invalid processing type: {new_type}. Must be one of: '
                '`self.ProcessingTypes`.'
            )
        self._processing_type = new_type

    @property
    def processing_type_param1(self):
        """Processing type param1.

        For most processing types, this is a time interval in seconds, but for
        some types, it has a different meaning. Please, refer to the
        documentation of `processing_type` for details.
        """
        return self._processing_type_param1

    @processing_type_param1.setter
    def processing_type_param1(self, new_param):
        if not isinstance(new_param, (int, float)):
            raise _exceptions.TypeError(
                'expected argument of type int or float, got '
                + str(type(new_param))
            )
        self._processing_type_param1 = new_param

    @property
    def processing_type_param2(self):
        """Processing type param2.

        See docs for `processing_type`. For most processing types, this is not
        used, but for some types, it controls the number of standard
        deviations to consider in outlier filtering, with a default value of 3.
        """
        return self._processing_type_param2

    @processing_type_param2.setter
    def processing_type_param2(self, new_param):
        if not isinstance(new_param, (int, float)):
            raise _exceptions.TypeError(
                'expected argument of type int or float, got '
                + str(type(new_param))
            )
        self._processing_type_param2 = new_param

    def update(self, query_timeout=None):
        """Update."""
        self.connect()

        if query_timeout is not None:
            query_timeout0 = self.query_timeout
            self.query_timeout = query_timeout

        try:
            data = self.connector.get_data(
                self._pvname,
                self.time_start,
                self.time_stop,
                query_split_interval=self.query_split_interval,
                proc_type=self.processing_type,
                proc_type_param1=self.processing_type_param1,
                proc_type_param2=self.processing_type_param2,
            )
        finally:
            if query_timeout is not None:
                self.query_timeout = query_timeout0

        if not data:
            return
        self.set_data(**data)

    def gen_archviewer_url_link(
        self,
        pvnames=None,
        time_start=None,
        time_stop=None,
        time_ref=None,
        pvoptnrpts=None,
        pvcolors=None,
        pvusediff=False,
    ):
        """Generate a Archiver Viewer URL for the given PVs.

        Parameters
        ----------
        pvnames : iterable[str]
            Iterable of PV names to include in the viewer.
        time_start : datetime.datetime or siriuspy.clientarch.time.Time
            Start time of the interval to display.
        time_stop : datetime.datetime or siriuspy.clientarch.time.Time
            Stop time of the interval to display.
        time_ref : datetime.datetime or siriuspy.clientarch.time.Time, optional
            reference time used when enabling the diff view.
        pvoptnrpts : iterable[int] or Int, optional
            Iterable with optimization point counts for each PV (0 or None
            means no optimization). Must have the same length as `pvnames` or
            be a single integer applied to all PVs.
        pvcolors : iterable[str or None] or str, optional
            Iterable with hex color strings (e.g. "#00ff00") or None for
            each PV. Must have the same length as `pvnames` or be a single
            string applied to all PVs.
        pvusediff : iterable[bool] or bool, optional
            Iterable indicating whether to enable the diff option for each PV.
            Must have the same length as `pvnames` or
            be a single bool applied to all PVs.

        Returns
        -------
        str
            A full Archiver Viewer URL containing the compressed PV
            configuration.

        """
        pvnames = pvnames or [self._pvname]
        url = super().gen_archviewer_url_link(
            pvnames=pvnames,
            time_start=time_start,
            time_stop=time_stop,
            time_ref=time_ref,
            pvoptnrpts=pvoptnrpts,
            pvcolors=pvcolors,
            pvusediff=pvusediff,
        )
        return url

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
                query_split_interval (int): interval to split queries.
                query_max_concurrency (int): max concurrency for queries.
                query_timeout (float): timeout for queries.
                processing_type (str): type of processing for queries.
                processing_type_param1 (float or int): param 1 for processing.
                processing_type_param2 (float or int): param 2 for processing.
                data (dict): dictionary with archiver data  with fields:
                    value (numpy.ndarray): values of the PV.
                    timestamp (numpy.ndarray): timestamps of the PV.
                    status (numpy.ndarray): status of the PV.
                    severity (numpy.ndarray): severity of the PV.

        """
        return dict(
            server_url=self.connector.server_url,
            pvname=self.pvname,
            timestamp_start=self.time_start.timestamp(),
            timestamp_stop=self.time_stop.timestamp(),
            query_split_interval=self.query_split_interval,
            query_max_concurrency=self.query_max_concurrency,
            query_timeout=self.query_timeout,
            processing_type=self.processing_type,
            processing_type_param1=self.processing_type_param1,
            processing_type_param2=self.processing_type_param2,
            data=dict(
                timestamp=self.timestamp,
                value=self.value,
                status=self.status,
                severity=self.severity,
            ),
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
        pvdata.time_start = infos['timestamp_start']
        pvdata.time_stop = infos['timestamp_stop']
        pvdata.query_split_interval = infos['query_split_interval']
        pvdata.query_max_concurrency = infos['query_max_concurrency']
        pvdata.query_timeout = infos['query_timeout']
        pvdata.processing_type = infos['processing_type']
        pvdata.processing_type_param1 = infos['processing_type_param1']
        pvdata.processing_type_param2 = infos['processing_type_param2']
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

    ProcessingTypes = _ClientArchiver.ProcessingTypes

    def __init__(self, pvnames, connector=None, beamline_data=False):
        """Initialize."""
        super().__init__(connector, beamline_data=beamline_data)
        self._pvnames = pvnames
        self._pvdata = self._init_pvdatas(pvnames, self.connector)

    def __str__(self):
        """."""
        stg = ''
        stg += 'Connector Properties:\n'
        stg += '    {:<30s}: {:d}\n'.format(
            'query_max_concurrency', self.query_max_concurrency
        )
        stg += '    {:<30s}: {:.1f}\n'.format(
            'query_timeout [s]', self.query_timeout
        )
        stg += '\nPV Data Properties:\n'
        tmpl = '    {:<30s} {:^30s} {:^30s} {:^15s} '
        tmpl += '{:^12s} {:^10s} {:^10s} {:^10s}\n'
        stg += tmpl.format(
            'PV Name',
            'Time Start',
            'Time Stop',
            'Bin Interval',
            'Proc. Type',
            'Param1',
            'Param2',
            'Data Length',
        )
        for pvn, pvd in self._pvdata.items():
            prty = pvd.processing_type
            prty = prty if prty else "''"

            pr1 = pvd.processing_type_param1
            pr1s = 'None' if pr1 is None else f'{pr1:d}'
            if prty != self.ProcessingTypes.SelectByChange:
                pr1s = 'None' if pr1 is None else f'{pr1:.1g}'
            elif prty != self.ProcessingTypes.None_:
                pr1s = 'N/A'

            pr2 = 'N/A'
            if prty in (
                self.ProcessingTypes.Outliers,
                self.ProcessingTypes.IgnoreOutliers,
            ):
                pr2 = f'{pvd.processing_type_param2:.1g}'

            dlen = 'Not Loaded'
            if pvd.timestamp is not None:
                dlen = f'{len(pvd.timestamp):d}'

            stg += tmpl.format(
                pvn,
                pvd.time_start.get_iso8601(),
                pvd.time_stop.get_iso8601(),
                f'{pvd.query_split_interval:d}',
                prty,
                pr1s,
                pr2,
                dlen,
            )
        return stg

    # -------- Properties to control data acquisition and processing --------

    @property
    def pvnames(self):
        """PV names."""
        return _dcopy(self._pvnames)

    @pvnames.setter
    def pvnames(self, new_pvnames):
        self._pvnames = new_pvnames
        self._pvdata = self._init_pvdatas(new_pvnames, self.connector)

    @property
    def query_split_interval(self):
        """Queries larger than this interval will be split.

        If set to 0 or None, no splitting will be done.
        """
        qry = [self._pvdata[pvn].query_split_interval for pvn in self._pvnames]
        if len(set(qry)) == 1:
            return qry[0]
        return qry

    @query_split_interval.setter
    def query_split_interval(self, value):
        if value is None:
            value = 0
        if isinstance(value, (int, float)):
            value = len(self._pvnames) * [int(value)]
        if len(value) != len(self._pvnames):
            raise ValueError('value must have the same length as pvnames')

        for pvn, val in zip(self._pvnames, value):  # noqa: B905
            self._pvdata[pvn].query_split_interval = val

    @property
    def query_max_concurrency(self):
        """Query max concurrency.

        This is a global setting for the connector, so all PVData objects
        share it, but we allow it to be set through PVDataSet for convenience.

        """
        return self.connector.query_max_concurrency

    @query_max_concurrency.setter
    def query_max_concurrency(self, new_intvl):
        self.connector.query_max_concurrency = new_intvl

    @property
    def time_start(self):
        """Start time."""
        tstt = [self._pvdata[pvn].time_start for pvn in self._pvnames]
        if len(set(tstt)) == 1:
            return tstt[0]
        return tstt

    @time_start.setter
    def time_start(self, value):
        """Accept any value that can be converted to a Time object."""
        try:
            value = _Time(value)
            value = [value] * len(self._pvnames)
        except Exception:  # noqa: S110
            pass
        if len(value) != len(self._pvnames):
            raise ValueError('value must have the same length as pvnames')

        for pvn, val in zip(self._pvnames, value):  # noqa: B905
            self._pvdata[pvn].time_start = val

    @property
    def time_stop(self):
        """Stop time."""
        tstt = [self._pvdata[pvn].time_stop for pvn in self._pvnames]
        if len(set(tstt)) == 1:
            return tstt[0]
        return tstt

    @time_stop.setter
    def time_stop(self, value):
        """Accept any value that can be converted to a Time object."""
        try:
            value = _Time(value)
            value = [value] * len(self._pvnames)
        except Exception:  # noqa: S110
            pass
        if len(value) != len(self._pvnames):
            raise ValueError('value must have the same length as pvnames')

        for pvn, val in zip(self._pvnames, value):  # noqa: B905
            self._pvdata[pvn].time_stop = val

    @property
    def processing_type(self):
        """Data processing type to use for query.

        For details on each operator, please, refer to the section
        Processing of data of the following page:
        https://epicsarchiver.readthedocs.io/en/latest/user/userguide.html

        The options implemented here are:

        The options below do not take any aditional parameter:
            '' --> No processing, raw data is returned.
            'ncount' --> total number of updates in the whole interval.

        All types of processing below, require an aditional parameter,
        controlled by the input `proc_type_param1`. Then the
        refered statistics will be performed within this interval:
            'mean'
            'median'
            'std'
            'variance'
            'popvariance' --> population variance.
            'kurtosis'
            'skewness'
            'mini' --> same as min, which is also accepted by the archiver.
            'maxi' --> same as max, which is also accepted by the archiver.
            'jitter' --> std / mean for each bin.
            'count' --> number of updates in each bin.
            'firstSample'
            'lastSample'
            'firstFill' --> see url for difference to `'firstSample'`.
            'lastFill' --> see url for difference to `'lastSample'`.
            'linear' --> not sure, look at the archiver docs.
            'loess' --> not sure, look at the archiver docs.

        The processing below also use an aditional parameter, but its
        meaning is different from the statistics above:
            'optimized' --> the parameter means the total number of points
                            to be returned, instead of the time interval.
            'optimLastSample' --> close to 'opimized'. See docs for diff.
            'nth' --> return every nth sample.
            'deadBand' --> similar to ADEL. Only return when values change
                by a certain amount.

        For both statistics below a second parameter is needed to configure
        acquisition, controlled by `proc_type_param2`. This
        parameter controls the number of standard deviations to consider
        in the filtering bellow. The default of this parameter is 3.0:
            'ignoreflyers' --> whether to ignore outliers
            'flyers' --> only return outliers
        """
        proc = [self._pvdata[pvn].processing_type for pvn in self._pvnames]
        if len(set(proc)) == 1:
            return proc[0]
        return proc

    @processing_type.setter
    def processing_type(self, value):
        if isinstance(value, str):
            value = len(self._pvnames) * [value]
        if len(value) != len(self._pvnames):
            raise ValueError('value must have the same length as pvnames')

        for pvn, val in zip(self._pvnames, value):  # noqa: B905
            self._pvdata[pvn].processing_type = val

    @property
    def processing_type_param1(self):
        """Processing type param1."""
        param = [
            self._pvdata[pvn].processing_type_param1 for pvn in self._pvnames
        ]
        if len(set(param)) == 1:
            return param[0]
        return param

    @processing_type_param1.setter
    def processing_type_param1(self, value):
        if value is None or isinstance(value, (int, float)):
            value = len(self._pvnames) * [value]
        if len(value) != len(self._pvnames):
            raise ValueError('value must have the same length as pvnames')

        for pvn, val in zip(self._pvnames, value):  # noqa: B905
            self._pvdata[pvn].processing_type_param1 = val

    @property
    def processing_type_param2(self):
        """Processing type param2."""
        param = [
            self._pvdata[pvn].processing_type_param2 for pvn in self._pvnames
        ]
        if len(set(param)) == 1:
            return param[0]
        return param

    @processing_type_param2.setter
    def processing_type_param2(self, value):
        if value is None or isinstance(value, (int, float)):
            value = len(self._pvnames) * [value]
        if len(value) != len(self._pvnames):
            raise ValueError('value must have the same length as pvnames')

        for pvn, val in zip(self._pvnames, value):  # noqa: B905
            self._pvdata[pvn].processing_type_param2 = val

    @property
    def is_archived(self):
        """Is archived."""
        self.connect()
        for pvn in self._pvnames:
            if self.connector.get_pv_details(pvn) is None:
                return False
        return True

    @property
    def not_archived(self):
        """PVs not being archived."""
        self.connect()
        not_archived = list()
        for pvn in self._pvnames:
            if self.connector.get_pv_details(pvn) is None:
                not_archived.append(pvn)
        return not_archived

    @property
    def archived(self):
        """PVs being archived."""
        archived = set(self._pvnames) - set(self.not_archived)
        return list(archived)

    def update(self, query_timeout=None):
        """Update."""
        self.connect()

        if query_timeout is not None:
            query_timeout0 = self.query_timeout
            self.query_timeout = query_timeout

        all_urls = []
        pvn2idcs = dict()
        for pvn in self._pvnames:
            pvd = self._pvdata[pvn]
            urls = self.connector.get_request_url_for_get_data(
                pvn,
                pvd.time_start,
                pvd.time_stop,
                query_split_interval=pvd.query_split_interval,
                proc_type=pvd.processing_type,
                proc_type_param1=pvd.processing_type_param1,
                proc_type_param2=pvd.processing_type_param2,
                return_pvn2idcs_dict=False,
            )
            urls = [urls] if isinstance(urls, str) else urls
            ini = len(all_urls)
            all_urls.extend(urls)
            end = len(all_urls)
            pvn2idcs[pvn] = _np.arange(ini, end)

        try:
            resps = self.connector.make_request(all_urls)
        finally:
            if query_timeout is not None:
                self.query_timeout = query_timeout0

        if not resps:
            return None

        data = self.connector.process_resquest_of_get_data(
            self._pvnames, resps, pvn2idcs
        )

        if not data:
            return
        if len(self._pvnames) == 1:
            pvname = self._pvnames[0]
            data = {pvname: data}
        for pvname in self._pvnames:
            self._pvdata[pvname].set_data(**data[pvname])

    def gen_archviewer_url_link(
        self,
        pvnames=None,
        time_start=None,
        time_stop=None,
        time_ref=None,
        pvoptnrpts=None,
        pvcolors=None,
        pvusediff=False,
    ):
        """Generate a Archiver Viewer URL for the given PVs.

        Parameters
        ----------
        pvnames : iterable[str]
            Iterable of PV names to include in the viewer.
        time_start : datetime.datetime or siriuspy.clientarch.time.Time
            Start time of the interval to display.
        time_stop : datetime.datetime or siriuspy.clientarch.time.Time
            Stop time of the interval to display.
        time_ref : datetime.datetime or siriuspy.clientarch.time.Time, optional
            reference time used when enabling the diff view.
        pvoptnrpts : iterable[int] or Int, optional
            Iterable with optimization point counts for each PV (0 or None
            means no optimization). Must have the same length as `pvnames` or
            be a single integer applied to all PVs.
        pvcolors : iterable[str or None] or str, optional
            Iterable with hex color strings (e.g. "#00ff00") or None for
            each PV. Must have the same length as `pvnames` or be a single
            string applied to all PVs.
        pvusediff : iterable[bool] or bool, optional
            Iterable indicating whether to enable the diff option for each PV.
            Must have the same length as `pvnames` or
            be a single bool applied to all PVs.

        Returns
        -------
        str
            A full Archiver Viewer URL containing the compressed PV
            configuration.

        """
        pvnames = pvnames or self._pvnames
        time_start = time_start or self.time_start
        time_stop = time_stop or self.time_stop
        url = super().gen_archviewer_url_link(
            pvnames=pvnames,
            time_start=time_start,
            time_stop=time_stop,
            time_ref=time_ref,
            pvoptnrpts=pvoptnrpts,
            pvcolors=pvcolors,
            pvusediff=pvusediff,
        )
        return url

    def _init_pvdatas(self, pvnames, connector):
        return {pvname: PVData(pvname, connector) for pvname in pvnames}

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
        data = dict(server_url=self.connector.server_url, pvnames=self.pvnames)
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
        for i, pvdata in enumerate(pvdataset):
            pvdata.from_dict(**info['pvdata_info'][i])
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
