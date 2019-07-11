#!/usr/bin/env python-sirius
"""Fetcher module."""


import requests
from urllib import parse as _parse
# import json

import siriuspy.envars as _envars


# See https://slacmshankar.github.io/epicsarchiver_docs/userguide.html


class ClientArchiver:
    """Archiver Data Fetcher class."""

    SERVER_URL = _envars.server_url_archiver
    ENDPOINT = '/mgmt/bpl'

    def __init__(self, server_url=None):
        """."""
        self.session = None
        self._url = server_url or self.SERVER_URL

    def login(self, username, password):
        headers = {"User-Agent": "Mozilla/5.0"}
        payload = {"username": username, "password": password}
        self.session = requests.Session()
        url = self._create_url(method='login')
        response = self.session.post(
            url, headers=headers, data=payload, verify=False)
        return b"authenticated" in response.content

    def getPVsInfo(self, pvnames):
        if isinstance(pvnames, (list, tuple)):
            pvnames = ','.join(pvnames)
        url = self._create_url(method='getPVStatus', pv=pvnames)
        return self.session.get(url).json()

    def getAllPVs(self, pvnames):
        if isinstance(pvnames, (list, tuple)):
            pvnames = ','.join(pvnames)
        url = self._create_url(method='getAllPVs', pv=pvnames, limit='-1')
        return self.session.get(url).json()

    def deletePVs(self, pvnames):
        for pvname in pvnames:
            url = self._create_url(
                method='deletePV', pv=pvname, deleteData='true')
            self.session.get(url)

    def pausePVs(self, pvnames):
        for pvname in pvnames:
            url = self._create_url(method='pauseArchivingPV', pv=pvnames)
            self.session.get(url)

    def renamePV(self, oldname, newname):
        url = self._create_url(method='renamePV', pv=oldname, newname=newname)
        self.session.get(url)

    def resumePVs(self, pvnames):
        for pvname in pvnames:
            url = self._create_url(method='resumeArchivingPV', pv=pvname)
            self.session.get(url)

    def getData(self, pvname, timestamp_start, timestamp_stop):
        """Get archiver data.

        pvname -- name of pv.
        timestamp_start -- timestamp of interval start
                           Example: (2019-05-23T13:32:27.570Z)
        timestamp_stop -- timestamp of interval start
                           Example: (2019-05-23T14:32:27.570Z)
        """
        tstart = _parse.quote(timestamp_start)
        tstop = _parse.quote(timestamp_stop)
        url = self._create_url(
            method='getData.json', pv=pvname, **{'from': tstart, 'to': tstop})
        req = self.session.get(url)
        data = req.json()[0]['data']
        value = [v['val'] for v in data]
        timestamp = [v['secs'] + v['nanos']/1.0e9 for v in data]
        status = [v['status'] for v in data]
        severity = [v['severity'] for v in data]
        return timestamp, value, status, severity

    def _create_url(self, method, **kwargs):
        """."""
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
