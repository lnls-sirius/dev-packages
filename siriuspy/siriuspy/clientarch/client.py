"""Fetcher module.

See
    https://slacmshankar.github.io/epicsarchiver_docs/userguide.html
    http://slacmshankar.github.io/epicsarchiver_docs/details.html
    http://slacmshankar.github.io/epicsarchiver_docs/api/mgmt_scriptables.html
"""

import asyncio as _asyncio
import logging as _log
import math as _math
import urllib as _urllib
from datetime import timedelta as _timedelta
from threading import Thread as _Thread
from urllib.parse import quote as _quote

import numpy as _np
import urllib3 as _urllib3
from aiohttp import (
    client_exceptions as _aio_exceptions,
    ClientSession as _ClientSession
)
from mathphys.functions import get_namedtuple as _get_namedtuple

try:
    from lzstring import LZString as _LZString
except ModuleNotFoundError:
    _LZString = None

from .. import envars as _envars
from . import exceptions as _exceptions
from .time import get_time_intervals as _get_time_intervals, Time as _Time


class ClientArchiver:
    """Archiver Data Fetcher class."""

    DEF_QUERY_BIN_INTERVAL = 12 * 60 * 60  # 12h
    DEFAULT_TIMEOUT = 5.0  # [s]
    SERVER_URL = _envars.SRVURL_ARCHIVER
    ENDPOINT = '/mgmt/bpl'

    _REPORTS = {
        'DisconnectedPVs': 'getCurrentlyDisconnectedPVs',
        'PausedPVs': 'getPausedPVsReport',
        'EventRate': 'getEventRateReport',
        'StorageRate': 'getStorageRateReport',
        'RecentlyAddedPVs': 'getRecentlyAddedPVs',
        'RecentlyModifiedPVs': 'getRecentlyModifiedPVs',
        'LostConnections': 'getLostConnectionsReport',
        'LastKnownTimestamps': 'getSilentPVsReport',
        'DroppedEventsWrongTimestamp': 'getPVsByDroppedEventsTimestamp',
        'DroppedEventsBufferOverflow': 'getPVsByDroppedEventsBuffer',
        'DroppedEventsTypeChange': 'getPVsByDroppedEventsTypeChange',
    }
    ReportTypes = _get_namedtuple(
        'ReportTypes', _REPORTS.keys(), _REPORTS.values()
    )
    _PROC_TYPES = {
        'None_': '',
        'TotalCount': 'ncount',
        'Mean': 'mean',
        'Median': 'median',
        'STD': 'std',
        'Variance': 'variance',
        'Popvariance': 'popvariance',
        'Kurtosis': 'kurtosis',
        'Skewness': 'skewness',
        'Min': 'mini',
        'Max': 'maxi',
        'STDoverMean': 'jitter',
        'Count': 'count',
        'FirstSample': 'firstSample',
        'LastSample': 'lastSample',
        'FirstFill': 'firstFill',
        'LastFill': 'lastFill',
        'Linear': 'linear',
        'Loess': 'loess',
        'Optimized': 'optimized',
        'OptimLastSample': 'optimLastSample',
        'NthSample': 'nth',
        'SelectByChange': 'deadBand',
        'IgnoreOutliers': 'ignoreflyers',
        'Outliers': 'flyers',
    }
    ProcessingTypes = _get_namedtuple(
        'ProcessingTypes', _PROC_TYPES.keys(), _PROC_TYPES.values()
    )

    def __delete__(self):
        """Turn off thread when deleting."""
        self.shutdown()

    def __init__(self, server_url=None, timeout=None):
        """Initialize."""
        timeout = timeout or ClientArchiver.DEFAULT_TIMEOUT
        self.session = None
        self._timeout = timeout
        self._url = server_url or self.SERVER_URL
        self._request_url = None
        self._thread = self._loop = None
        self._query_bin_interval = self.DEF_QUERY_BIN_INTERVAL
        self.connect()
        _urllib3.disable_warnings(_urllib3.exceptions.InsecureRequestWarning)

    def connect(self):
        """Starts bg. event loop in a separate thread.

        Raises:
            RuntimeError: when library is alread connected.
        """
        if self._loop_alive():
            return

        self._loop = _asyncio.new_event_loop()
        self._thread = _Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

    def shutdown(self, timeout=5):
        """Safely stops the bg. loop and waits for the thread to exit."""
        if not self._loop_alive():
            return

        # 1. Cancel all pending tasks in the loop (to avoid ResourceWarnings)
        self._loop.call_soon_threadsafe(self._cancel_all_tasks)

        # 2. Schedule the loop to stop processing
        self._loop.call_soon_threadsafe(self._loop.stop)

        # 3. Wait for the thread to actually finish
        self._thread.join(timeout=timeout)
        if self._thread.is_alive():
            print('Warning: Background thread did not stop in time.')

    @property
    def connected(self):
        """Connected."""
        if not self._loop_alive():
            return False
        try:
            resp = self.make_request(self._url, return_json=False)
            return resp.status == 200
        except _urllib.error.URLError:
            return False

    @property
    def timeout(self):
        """Connection timeout."""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        """Set connection timeout."""
        self._timeout = float(value)

    @property
    def server_url(self):
        """Return URL of the Archiver server.

        Returns:
            str: URL of the server.

        """
        return self._url

    @server_url.setter
    def server_url(self, url):
        """Set the new server URL. Logs out if needed.

        Args:
            url (str): New server URL to use.

        """
        self.logout()
        self._url = url

    @property
    def query_bin_interval(self):
        """Query bin interval."""
        return self._query_bin_interval

    @query_bin_interval.setter
    def query_bin_interval(self, new_intvl):
        if not isinstance(new_intvl, (float, int)):
            raise _exceptions.TypeError(
                'expected argument of type float or int, got '
                + str(type(new_intvl))
            )
        self._query_bin_interval = new_intvl

    @property
    def last_requested_url(self):
        """."""
        return self._request_url

    def login(self, username, password):
        """Open login session."""
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {'username': username, 'password': password}
        url = self._create_url(method='login')
        coro = self._create_session(
            url, headers=headers, payload=payload, ssl=False
        )
        ret = self._run_sync_coro(coro)
        if ret is not None:
            self.session, authenticated = ret
            if authenticated:
                print(
                    'Reminder: close connection after using this '
                    'session by calling logout method!'
                )
            else:
                self.logout()
            return authenticated
        return False

    def logout(self):
        """Close login session."""
        if self.session:
            coro = self._close_session()
            resp = self._run_sync_coro(coro)
            self.session = None
            return resp
        return None

    def get_pvs_info(self, wildcards='*', max_num_pvs=-1):
        """Get PVs Info.

        Args:
            wildcards (str|list|tuple): Wildcards to match.
            max_num_pvs (int): Maximum number of PVs to return.

        Returns:
            list: List of dictionary with PVs details.

        """
        if isinstance(wildcards, (list, tuple)):
            wildcards = ','.join(wildcards)

        max_num_pvs = f'{int(max_num_pvs)}'
        url = self._create_url(
            method='getPVStatus', pv=wildcards, limit=max_num_pvs
        )
        resp = self.make_request(url, return_json=True)
        return None if not resp else resp

    def get_all_pvs(self, wildcards='*', max_num_pvs=-1):
        """Get All PVs matching wildcards.

        Args:
            wildcards (str|list|tuple): Wildcards to match.
            max_num_pvs (int): Maximum number of PVs to return.

        Returns:
            list: List of dictionary with PVs details.
        """
        if isinstance(wildcards, (list, tuple)):
            wildcards = ','.join(wildcards)

        max_num_pvs = f'{int(max_num_pvs)}'
        url = self._create_url(
            method='getAllPVs', pv=wildcards, limit=max_num_pvs
        )
        resp = self.make_request(url, return_json=True)
        return None if not resp else resp

    def delete_pvs(self, pvnames, delete_data=False):
        """Delete PVs."""
        if not isinstance(pvnames, (list, tuple)):
            pvnames = (pvnames,)

        delete_data = 'true' if delete_data else 'false'
        for pvname in pvnames:
            url = self._create_url(
                method='deletePV', pv=pvname, deleteData=delete_data
            )
            self.make_request(url, need_login=True)

    def get_report(self, report_name='PausedPVs', max_num_pvs=None):
        """Get Paused PVs Report.

        Args:
            report_name (str): Report name. Use self.ReportTypes to get
                all available reports.
            max_num_pvs (int): Maximum number of PVs to return.

        Returns:
            dict: Report results.

        """
        method = getattr(self.ReportTypes, report_name)
        if max_num_pvs is not None:
            max_num_pvs = f'{int(max_num_pvs)}'
            url = self._create_url(method=method, limit=max_num_pvs)
        else:
            url = self._create_url(method=method)

        resp = self.make_request(url, return_json=True)
        return None if not resp else resp

    def get_recently_modified_pvs(self, max_num_pvs=None, epoch_time=True):
        """Get list of PVs with recently modified PVTypeInfo.

        Currently version of the epics archiver appliance returns pvname
        list from oldest to newest modified timestamps.
        """
        resp = self.get_report(
            self,
            report_name=self.ReportTypes.RecentlyModifiedPVs,
            max_num_pvs=max_num_pvs,
        )

        # convert to epoch, if the case
        if resp and epoch_time:
            for item in resp:
                modtime = item['modificationTime'][
                    :-7
                ]  # remove ISO8601 offset
                epoch_time = _Time.conv_to_epoch(modtime, '%b/%d/%Y %H:%M:%S')
                item['modificationTime'] = epoch_time

        return None if not resp else resp

    def pause_pvs(self, pvnames):
        """Pause PVs."""
        if not isinstance(pvnames, (list, tuple)):
            pvnames = (pvnames,)
        for pvname in pvnames:
            url = self._create_url(method='pauseArchivingPV', pv=pvname)
            self.make_request(url, need_login=True)

    def rename_pv(self, oldname, newname):
        """Rename PVs."""
        url = self._create_url(method='renamePV', pv=oldname, newname=newname)
        return self.make_request(url, need_login=True)

    def resume_pvs(self, pvnames):
        """Resume PVs."""
        if not isinstance(pvnames, (list, tuple)):
            pvnames = (pvnames,)
        for pvname in pvnames:
            url = self._create_url(method='resumeArchivingPV', pv=pvname)
            self.make_request(url, need_login=True)

    def get_data(  # noqa: D417
        self,
        pvnames,
        timestamp_start,
        timestamp_stop,
        query_bin_interval=None,
        proc_type='',
        proc_type_param1=None,
        proc_type_param2=3.0,
    ):
        """Get archiver data.

        Args:
        pvnames (str|list|tuple): names of the PVs.
        timestamp_start (str|int|Time|list|tuple): start time for query.
            If it is a list or tuple, all PVs will be queried for each of
            the time intervals. In this case, it must have the same length
            as `timestamp_stop`.
        timestamp_stop (str|int|Time|list|tuple): stop time for query.
            If it is a list or tuple, all PVs will be queried for each of
            the time intervals. In this case, it must have the same length
            as `timestamp_start`.
        query_bin_interval (float): overwrites `self.query_bin_interval`.
            Defaults to `self.query_bin_interval`. Maximum interval for
            queries. If
                `timestamp_stop - timestamp_start > query_bin_interval`,
            it will be split into parallel queries.
        proc_type (str): data processing type to use for query. Defaults to
            ''. For details on each operator, please, refer to the section
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

        proc_type_param1 (int): First parameter for data processing. See
            `proc_type` for more details.
        proc_type_param2 (int): Second parameter for data processing. See
            `proc_type` for more details.

        Returns:
            dict: a dictionary with PV names as keys and data as values.

        """
        if isinstance(pvnames, str):
            pvnames = [pvnames]

        urls, pvn2idcs = self.get_request_url_for_get_data(
            pvnames,
            timestamp_start,
            timestamp_stop,
            query_bin_interval=query_bin_interval,
            proc_type=proc_type,
            proc_type_param1=proc_type_param1,
            proc_type_param2=proc_type_param2,
            return_pv2indcs_dict=True,
        )
        urls = [urls] if isinstance(urls, str) else urls

        resps = self.make_request(urls, return_json=True)
        if not resps:
            return None

        return self.process_resquest_of_get_data(pvnames, resps, pvn2idcs)

    def get_request_url_for_get_data(  # noqa: C901, D417
        self,
        pvnames,
        timestamp_start,
        timestamp_stop,
        query_bin_interval=None,
        proc_type=None,
        proc_type_param1=None,
        proc_type_param2=None,
        return_pvn2idcs_dict=False,
    ):
        """Get url for data request in `get_data` function.

        Args:
        pvnames (str|list|tuple): names of the PVs.
        timestamp_start (str|int|Time|list|tuple): start time for query.
            If it is a list or tuple, all PVs will be queried for each of
            the time intervals. In this case, it must have the same length
            as `timestamp_stop`.
        timestamp_stop (str|int|Time|list|tuple): stop time for query.
            If it is a list or tuple, all PVs will be queried for each of
            the time intervals. In this case, it must have the same length
            as `timestamp_start`.
        query_bin_interval (float): overwrites `self.query_bin_interval`.
            Defaults to `self.query_bin_interval`. Maximum interval for
            queries. If
                `timestamp_stop - timestamp_start > query_bin_interval`,
            it will be split into parallel queries.
        proc_type (str): data processing type to use for query. Defaults to
            ''. For details on each operator, please, refer to the section
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

        proc_type_param1 (int): First parameter for data processing. See
            `proc_type` for more details.
        proc_type_param2 (int): Second parameter for data processing. See
            `proc_type` for more details.
        return_pvn2idcs_dict (bool): whether to return a dictionary with
                PV names as keys and indices as values. Defaults to False.

        Returns:
            str|list|tuple: url or list of urls.
        """
        if isinstance(pvnames, str):
            pvnames = [pvnames]

        if not isinstance(timestamp_start, (list, tuple)):
            timestamp_start = [timestamp_start]
        if not isinstance(timestamp_stop, (list, tuple)):
            timestamp_stop = [timestamp_stop]

        if len(timestamp_start) != len(timestamp_stop):
            raise _exceptions.IndexError(
                '`timestamp_start` and `timestamp_stop` must have same length.'
            )

        bin_interval = query_bin_interval or self.query_bin_interval

        tstamps_start = []
        tstamps_stop = []
        for tst, tsp in zip(timestamp_start, timestamp_stop):  # noqa: B905
            try:
                tst = _Time(tst)
                tsp = _Time(tsp)
            except (TypeError, ValueError) as err:
                raise _exceptions.TypeError(
                    '`timestamp_start` and `timestamp_stop` must be either '
                    'timestamp string, integer timestamp or Time objects. '
                    'Or an iterable of these objects.'
                ) from err
            tstarts, tstops = _get_time_intervals(
                tst, tsp, bin_interval, return_isoformat=True
            )
            if isinstance(tstarts, (list, tuple)):
                tstamps_start.extend(tstarts)
                tstamps_stop.extend(tstops)
            else:
                tstamps_start.append(tstarts)
                tstamps_stop.append(tstops)

        pvname_orig = list(pvnames)
        if proc_type:
            process_str = proc_type
            if proc_type != 'ncount' and proc_type_param1 is not None:
                if 'deadBand' in process_str:
                    decim = -int(_math.log10(abs(proc_type_param1))) + 1
                    process_str += f'_{proc_type_param1:{max(0, decim)}f}'
                else:
                    process_str += f'_{int(proc_type_param1):d}'
                if 'flyers' in proc_type and proc_type_param2 is not None:
                    process_str += f'_{proc_type_param2:.2f}'
            pvnames = [process_str + '(' + pvn + ')' for pvn in pvnames]

        pvn2idcs = dict()
        all_urls = list()
        for i, pvn in enumerate(pvnames):
            urls = []
            for tst, tsp in zip(tstamps_start, tstamps_stop):  # noqa: B905
                urls.append(
                    self._create_url(
                        method='getData.json',
                        pv=pvn,
                        **{
                            'from': _urllib.parse.quote(tst),
                            'to': _urllib.parse.quote(tsp),
                        },
                    )
                )
            ini = len(all_urls)
            all_urls.extend(urls)
            end = len(all_urls)
            pvn2idcs[pvname_orig[i]] = _np.arange(ini, end)

        all_urls = all_urls[0] if len(all_urls) == 1 else all_urls
        if return_pvn2idcs_dict:
            return all_urls, pvn2idcs
        return all_urls

    def process_resquest_of_get_data(self, pvnames, resps, pvn2idcs):
        """Process result of `self.get_data` request.

        Args:
            pvnames (list): list of PV names envolved in request.
            resps (dict): output of `self.make_request` called from
                `self.get_data`.
            pvn2idcs (dict): list of pvnames to indices in `resps`.

        Returns:
            pvn2resp (dict): dictionary with PVs data.
        """
        pvn2resp = dict()
        for pvn, idcs in pvn2idcs.items():
            _ts, _vs = _np.array([]), list()
            _st, _sv = _np.array([]), _np.array([])
            for idx in idcs:
                resp = resps[idx]
                if not resp:
                    continue
                data = resp[0]['data']
                _ts = _np.r_[
                    _ts, [v['secs'] + v['nanos'] / 1.0e9 for v in data]
                ]
                for val in data:
                    _vs.append(val['val'])
                _st = _np.r_[_st, [v['status'] for v in data]]
                _sv = _np.r_[_sv, [v['severity'] for v in data]]
            if not _ts.size:
                timestamp = value = status = severity = None
            else:
                _, _tsidx = _np.unique(_ts, return_index=True)
                timestamp = _ts[_tsidx],
                status = _st[_tsidx],
                severity = _sv[_tsidx],
                value = [_vs[i] for i in _tsidx]

            pvn2resp[pvn] = dict(
                timestamp=timestamp,
                value=value,
                status=status,
                severity=severity,
            )

        if len(pvnames) == 1:
            return pvn2resp[pvnames[0]]
        return pvn2resp

    def get_pv_details(self, pvname, get_request_url=False):
        """Get PV Details."""
        url = self._create_url(method='getPVDetails', pv=pvname)
        if get_request_url:
            return url
        resp = self.make_request(url, return_json=True)
        return None if not resp else resp

    def switch_to_online_data(self):
        """."""
        self.server_url = _envars.SRVURL_ARCHIVER
        self.session = None

    def switch_to_offline_data(self):
        """."""
        self.server_url = _envars.SRVURL_ARCHIVER_OFFLINE_DATA
        self.session = None

    def make_request(self, url, need_login=False, return_json=False):
        """Make request.

        Args:
            url (str|list|tuple): url or list of urls to request.
            need_login (bool): whether request requires login.
            return_json (bool): whether to return json response.

        Returns:
            dict: dictionary with response.
        """
        self._request_url = url
        coro = self._handle_request(
            url, return_json=return_json, need_login=need_login
        )
        return self._run_sync_coro(coro)

    @staticmethod
    def gen_archviewer_url_link(
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

        Notes
        -----
        - PV names and timestamps are URL-encoded and the
            resulting query string is compressed using LZString
            (compressToEncodedURIComponent).
        - The function expects the per-PV arguments (`pvoptnrpts`, `pvcolors`,
            `pvusediff`) to be iterables aligned with `pvnames`.
        """
        # Thanks to Rafael Lyra for the basis of this implementation!
        archiver_viewer_url = _envars.SRVURL_ARCHIVER_VIEWER + '/?pvConfig='
        args = ClientArchiver._process_url_link_args(
            pvnames, pvoptnrpts, pvcolors, pvusediff
        )
        pvoptnrpts, pvcolors, pvusediff = args
        pv_search = ''
        for idx in range(len(pvnames)):
            pv_search += 'pv='
            pvname = pvnames[idx]
            pvopt = pvoptnrpts[idx]
            color = pvcolors[idx]
            use_diff = pvusediff[idx]
            url_pvname = _quote(pvname)
            if pvopt > 0:
                pv_search += f'optimized_{pvopt}({url_pvname})'
            else:
                pv_search += url_pvname
            if time_ref is not None and use_diff:
                pv_search += '_diff'
            if color is not None:
                pv_search += f'__{color}'
            pv_search += '&'
        search_url = pv_search

        date_pattern = '%Y-%m-%dT%H:%M:%S.000Z'
        time_zone = _timedelta(hours=3)

        start = time_start + time_zone
        formatted_start = start.strftime(date_pattern)
        search_url += f'from={_quote(formatted_start)}&'

        stop = time_stop + time_zone
        formatted_end = stop.strftime(date_pattern)
        search_url += f'to={_quote(formatted_end)}&'

        if time_ref is not None:
            ref = time_ref + time_zone
            formatted_ref = ref.strftime(date_pattern)
            search_url += f'ref={_quote(formatted_ref)}'

        lz = _LZString()
        compressed_data = lz.compressToEncodedURIComponent(search_url)
        return archiver_viewer_url + compressed_data

    # ---------- auxiliary methods ----------

    @staticmethod
    def _process_url_link_args(pvnames, pvoptnrpts, pvcolors, pvusediff):
        """Process URL link arguments."""
        if pvoptnrpts is None:
            pvoptnrpts = [0] * len(pvnames)
        elif isinstance(pvoptnrpts, int):
            pvoptnrpts = [pvoptnrpts] * len(pvnames)
        if pvcolors is None:
            pvcolors = [None] * len(pvnames)
        elif isinstance(pvcolors, str):
            pvcolors = [pvcolors] * len(pvnames)
        pvcolors = pvcolors or [None] * len(pvnames)
        if isinstance(pvusediff, bool):
            pvusediff = [pvusediff] * len(pvnames)
        return pvoptnrpts, pvcolors, pvusediff

    def _loop_alive(self):
        """Check if thread is alive and loop is running."""
        return (
            self._thread is not None
            and self._thread.is_alive()
            and self._loop.is_running()
        )

    def _cancel_all_tasks(self):
        """Helper to cancel tasks (must be called from the loop's thread)."""
        if hasattr(_asyncio, 'all_tasks'):
            all_tasks = _asyncio.all_tasks(loop=self._loop)
        else:  # python 3.6
            all_tasks = _asyncio.Task.all_tasks(loop=self._loop)

        for task in all_tasks:
            task.cancel()

    def _run_event_loop(self):
        _asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_forever()
        finally:
            self._loop.close()

    def _create_url(self, method, **kwargs):
        """Create URL."""
        url = self._url + self.ENDPOINT
        if method.startswith('getData.json'):
            url = self._url + '/retrieval/data'

        url += '/' + method
        if kwargs:
            url += '?'
            url += '&'.join([f'{k}={v}' for k, v in kwargs.items()])
        return url

    def _run_sync_coro(self, coro):
        """Run an async coroutine synchronously, compatible with Jupyter."""
        if not self._thread.is_alive():
            raise RuntimeError('Library is shut down')
        future = _asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=self._timeout)

    # ---------- async methods ----------

    async def _handle_request(self, url, return_json=False, need_login=False):
        """Handle request."""
        if self.session is not None:
            response = await self._get_request_response(
                url, self.session, return_json
            )
        elif need_login:
            raise _exceptions.AuthenticationError('You need to login first.')
        else:
            async with _ClientSession() as sess:
                response = await self._get_request_response(
                    url, sess, return_json
                )
        return response

    async def _get_request_response(self, url, session, return_json):
        """Get request response."""
        url = [url] if isinstance(url, str) else url
        try:
            response = await _asyncio.gather(*[
                session.get(u, ssl=False, timeout=self._timeout)
                for u in url
            ])
            if any([not r.ok for r in response]):
                return None
            if return_json:
                jsons = list()
                for res in response:
                    try:
                        data = await res.json()
                        jsons.append(data)
                    except ValueError:
                        _log.error('Error with URL %s', res.url)
                        jsons.append(None)
                response = jsons
        except _asyncio.TimeoutError as err:
            raise _exceptions.TimeoutError(
                'Timeout reached. Try to increase `timeout`.'
            ) from err
        except _aio_exceptions.ClientPayloadError as err:
            raise _exceptions.PayloadError(
                "Payload Error. Increasing `timeout` won't help. "
                'Try decreasing query_bin_interval, or decrease the'
                'time interval for the aquisition.'
            ) from err

        if len(url) == 1:
            return response[0]
        return response

    async def _create_session(self, url, headers, payload, ssl):
        """Create session and handle login."""
        session = _ClientSession()
        async with session.post(
            url, headers=headers, data=payload, ssl=ssl, timeout=self._timeout
        ) as response:
            content = await response.content.read()
            authenticated = b'authenticated' in content
        return session, authenticated

    async def _close_session(self):
        """Close session."""
        return await self.session.close()
