#!/usr/bin/env python-sirius
"""Fetcher module."""


import requests
# import json

# See https://slacmshankar.github.io/epicsarchiver_docs/userguide.html


class ArchiverFetcher:
    """Archiver Data Fetcher class."""

    SERVER_URL = 'http://10.0.38.42/retrieval/data/'

    # https://en.wikipedia.org/wiki/Percent-encoding
    CHAR2PENC = {
        ':': '%23'
    }

    _FORM_DEFLT = 'json'
    _METHOD_DEFLT = 'getData'

    def __init__(self, form=None, method=None, server_url=SERVER_URL):
        """."""
        self._form = ArchiverFetcher._FORM_DEFLT if form is None else form
        self._method = ArchiverFetcher._METHOD_DEFLT \
            if method is None else method
        self._server_url = ArchiverFetcher.SERVER_URL \
            if server_url is None else server_url

    def get_data(self, pvname, timestamp_start, timestamp_stop):
        """Get archiver data.

        pvname -- name of pv.
        timestamp_start -- timestamp of interval start
                           Example: (2019-05-23T13:32:27.570Z)
        timestamp_stop -- timestamp of interval start
                           Example: (2019-05-23T14:32:27.570Z)
        """
        url = self.get_url(pvname, timestamp_start, timestamp_stop)
        req = requests.get(url, verify=False)
        data = req.json()[0]['data']
        value = [v['val'] for v in data]
        timestamp = [v['secs'] + v['nanos']/1.0e9 for v in data]
        status = [v['status'] for v in data]
        severity = [v['severity'] for v in data]
        return timestamp, value, status, severity

    def get_url(self, pvname, timestamp_start, timestamp_stop):
        """."""
        pvname = self.conv_str_2_percent_encoding(pvname)
        fmturl = '{}{}.{}?pv={}&from={}&to={}'
        url = fmturl.format(
            self._server_url, self._method, self._form,
            pvname, timestamp_start, timestamp_stop)
        return url

    @staticmethod
    def conv_str_2_percent_encoding(pvname):
        """."""
        pvname_new = pvname
        for key, value in ArchiverFetcher.CHAR2PENC.items():
            pvname_new.replace(key, value)
        return pvname_new
