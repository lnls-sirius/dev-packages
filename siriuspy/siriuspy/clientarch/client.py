#!/usr/bin/env python-sirius
"""Fetcher module.

See https://slacmshankar.github.io/epicsarchiver_docs/userguide.html
"""

from threading import Thread as _Thread
import asyncio as _asyncio
import urllib as _urllib
import ssl as _ssl
import urllib3 as _urllib3
from aiohttp import ClientSession as _ClientSession

import numpy as _np

from .. import envars as _envars
from . import exceptions as _exceptions


class ClientArchiver:
    """Archiver Data Fetcher class."""

    DEFAULT_TIMEOUT = 5.0  # [s]
    SERVER_URL = _envars.SRVURL_ARCHIVER
    ENDPOINT = '/mgmt/bpl'

    def __init__(self, server_url=None, timeout=None):
        """Initialize."""
        timeout = timeout or ClientArchiver.DEFAULT_TIMEOUT
        self.session = None
        self._timeout = timeout
        self._url = server_url or self.SERVER_URL
        self._ret = None
        # print('urllib3 InsecureRequestWarning disabled!')
        _urllib3.disable_warnings(_urllib3.exceptions.InsecureRequestWarning)

    @property
    def connected(self):
        """Connected."""
        try:
            status = _urllib.request.urlopen(
                self._url, timeout=self._timeout,
                context=_ssl.SSLContext()).status
            return status == 200
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

    def login(self, username, password):
        """Open login session."""
        headers = {"User-Agent": "Mozilla/5.0"}
        payload = {"username": username, "password": password}
        url = self._create_url(method='login')
        ret = self._run_async_event_loop(
            self._create_session,
            url, headers=headers, payload=payload, ssl=False)
        if ret is not None:
            self.session, authenticated = ret
            if authenticated:
                print('Reminder: close connection after using this '
                      'session by calling logout method!')
            else:
                self.logout()
            return authenticated
        return False

    def logout(self):
        """Close login session."""
        if self.session:
            resp = self._run_async_event_loop(self._close_session)
            self.session = None
            return resp
        return None

    def getPVsInfo(self, pvnames):
        """Get PVs Info."""
        if isinstance(pvnames, (list, tuple)):
            pvnames = ','.join(pvnames)
        url = self._create_url(method='getPVStatus', pv=pvnames)
        resp = self._make_request(url, return_json=True)
        return None if not resp else resp

    def getAllPVs(self, pvnames):
        """Get All PVs."""
        if isinstance(pvnames, (list, tuple)):
            pvnames = ','.join(pvnames)
        url = self._create_url(method='getAllPVs', pv=pvnames, limit='-1')
        resp = self._make_request(url, return_json=True)
        return None if not resp else resp

    def deletePVs(self, pvnames):
        """Delete PVs."""
        if not isinstance(pvnames, (list, tuple)):
            pvnames = (pvnames, )
        for pvname in pvnames:
            url = self._create_url(
                method='deletePV', pv=pvname, deleteData='true')
            self._make_request(url, need_login=True)

    def getPausedPVsReport(self):
        """Get Paused PVs Report."""
        url = self._create_url(method='getPausedPVsReport')
        resp = self._make_request(url, return_json=True)
        return None if not resp else resp

    def pausePVs(self, pvnames):
        """Pause PVs."""
        if not isinstance(pvnames, (list, tuple)):
            pvnames = (pvnames, )
        for pvname in pvnames:
            url = self._create_url(method='pauseArchivingPV', pv=pvname)
            self._make_request(url, need_login=True)

    def renamePV(self, oldname, newname):
        """Rename PVs."""
        url = self._create_url(method='renamePV', pv=oldname, newname=newname)
        return self._make_request(url, need_login=True)

    def resumePVs(self, pvnames):
        """Resume PVs."""
        if not isinstance(pvnames, (list, tuple)):
            pvnames = (pvnames, )
        for pvname in pvnames:
            url = self._create_url(method='resumeArchivingPV', pv=pvname)
            self._make_request(url, need_login=True)

    def getData(self, pvname, timestamp_start, timestamp_stop,
                process_type='', interval=None, stddev=None,
                get_request_url=False):
        """Get archiver data.

        pvname -- name of pv.
        timestamp_start -- timestamp of interval start
                           Example: '2019-05-23T13:32:27.570Z'
        timestamp_stop -- timestamp of interval stop
                           Example: '2019-05-23T13:32:27.570Z'
        process_type -- data processing type to use. Can be:
                     '', 'mean', 'median', 'std', 'variance',
                     'popvariance', 'kurtosis', 'skewness'
                     'mini', 'maxi', 'jitter', 'count', 'ncount',
                     'firstSample', 'lastSample', 'firstFill', 'lastFill',
                     'nth', 'ignoreflyers' or 'flyers'
        interval -- interval of the bin of data, in seconds
        stddev -- number of standard deviations.
                  argument used in processing 'ignoreflyers' and 'flyers'.
        """
        if isinstance(pvname, str):
            pvname = [pvname, ]
        if isinstance(timestamp_start, str):
            timestamp_start = [timestamp_start, ]
        if isinstance(timestamp_stop, str):
            timestamp_stop = [timestamp_stop, ]
        if not isinstance(timestamp_start, (list, tuple)) or \
                not isinstance(timestamp_stop, (list, tuple)):
            raise _exceptions.TypeError(
                "'timestampstart' and 'timestamp_stop' arguments must be "
                "timestamp strings or iterable.")

        pvname_orig = list(pvname)
        if process_type:
            process_str = process_type
            if interval is not None:
                process_str += '_' + str(int(interval))
                if 'flyers' in process_type and stddev is not None:
                    process_str += '_' + str(int(stddev))
            pvname = [process_str+'('+pvn+')' for pvn in pvname]

        if get_request_url:
            tstart = _urllib.parse.quote(timestamp_start[0])
            tstop = _urllib.parse.quote(timestamp_stop[-1])
            url = [self._create_url(
                method='getData.json', pv=pvn,
                **{'from': tstart, 'to': tstop})
                   for pvn in pvname]
            return url[0] if len(pvname) == 1 else url

        pvn2idcs = dict()
        all_urls = list()
        for i, pvn in enumerate(pvname):
            urls = []
            for tstart, tstop in zip(timestamp_start, timestamp_stop):
                urls.append(self._create_url(
                    method='getData.json', pv=pvn,
                    **{'from': _urllib.parse.quote(tstart),
                       'to': _urllib.parse.quote(tstop)}))
            ini = len(all_urls)
            all_urls.extend(urls)
            end = len(all_urls)
            pvn2idcs[pvname_orig[i]] = _np.arange(ini, end)

        resps = self._make_request(all_urls, return_json=True)
        if resps is None:
            return None

        pvn2resp = dict()
        for pvn, idcs in pvn2idcs.items():
            _ts, _vs = _np.array([]), list()
            _st, _sv = _np.array([]), _np.array([])
            for idx in idcs:
                resp = resps[idx]
                if not resp:
                    continue
                data = resp[0]['data']
                _ts = _np.r_[_ts, [v['secs'] + v['nanos']/1.0e9 for v in data]]
                for val in data:
                    _vs.append(val['val'])
                _st = _np.r_[_st, [v['status'] for v in data]]
                _sv = _np.r_[_sv, [v['severity'] for v in data]]
            if not _ts.size:
                timestamp, value, status, severity = [None, None, None, None]
            else:
                _, _tsidx = _np.unique(_ts, return_index=True)
                timestamp, status, severity = \
                    _ts[_tsidx], _st[_tsidx], _sv[_tsidx]
                value = [_vs[i] for i in _tsidx]

            pvn2resp[pvn] = dict(
                timestamp=timestamp, value=value, status=status,
                severity=severity)

        if len(pvname) == 1:
            return pvn2resp[pvname_orig[0]]
        return pvn2resp

    def getPVDetails(self, pvname, get_request_url=False):
        """Get PV Details."""
        url = self._create_url(
            method='getPVDetails', pv=pvname)
        if get_request_url:
            return url
        resp = self._make_request(url, return_json=True)
        return None if not resp else resp

    # ---------- auxiliary methods ----------

    def _make_request(self, url, need_login=False, return_json=False):
        """Make request."""
        response = self._run_async_event_loop(
            self._handle_request,
            url, return_json=return_json, need_login=need_login)
        return response

    def _create_url(self, method, **kwargs):
        """Create URL."""
        url = self._url
        if method.startswith('getData.json'):
            url += '/retrieval/data'
        else:
            url += self.ENDPOINT
        url += '/' + method
        if kwargs:
            url += '?'
            url += '&'.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
        return url

    # ---------- async methods ----------
    def _run_async_event_loop(self, *args, **kwargs):
        # NOTE: Run the asyncio commands in a separated Thread to isolate
        # their EventLoop from the external environment (important for class
        # to work within jupyter notebook environment).
        _thread = _Thread(
            target=self._thread_run_async_event_loop,
            daemon=True, args=args, kwargs=kwargs)
        _thread.start()
        _thread.join()
        return self._ret

    def _thread_run_async_event_loop(self, func, *args, **kwargs):
        """Get event loop."""
        close = False
        try:
            loop = _asyncio.get_event_loop()
        except RuntimeError as error:
            if 'no current event loop' in str(error):
                loop = _asyncio.new_event_loop()
                _asyncio.set_event_loop(loop)
                close = True
            else:
                raise error
        try:
            self._ret = loop.run_until_complete(func(*args, **kwargs))
        except _asyncio.TimeoutError:
            raise _exceptions.TimeoutError

        if close:
            loop.close()

    async def _handle_request(
            self, url, return_json=False, need_login=False):
        """Handle request."""
        if self.session is not None:
            response = await self._get_request_response(
                url, self.session, return_json)
        elif need_login:
            raise _exceptions.AuthenticationError('You need to login first.')
        else:
            async with _ClientSession() as sess:
                response = await self._get_request_response(
                    url, sess, return_json)
        return response

    async def _get_request_response(self, url, session, return_json):
        """Get request response."""
        try:
            if isinstance(url, list):
                response = await _asyncio.gather(
                    *[session.get(u, ssl=False, timeout=self._timeout)
                      for u in url])
                if any([not r.ok for r in response]):
                    return None
                if return_json:
                    response = await _asyncio.gather(
                        *[r.json() for r in response])
            else:
                response = await session.get(
                    url, ssl=False, timeout=self._timeout)
                if not response.ok:
                    return None
                if return_json:
                    response = await response.json()
        except _asyncio.TimeoutError as err_msg:
            raise _exceptions.TimeoutError(err_msg)
        return response

    async def _create_session(self, url, headers, payload, ssl):
        """Create session and handle login."""
        session = _ClientSession()
        async with session.post(
                url, headers=headers, data=payload, ssl=ssl,
                timeout=self._timeout) as response:
            content = await response.content.read()
            authenticated = b"authenticated" in content
        return session, authenticated

    async def _close_session(self):
        """Close session."""
        return await self.session.close()
