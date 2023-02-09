"""IOC Search module."""

import re as _re
from threading import Lock as _Lock
import yaml as _yaml

from .. import clientweb as _web


class IOCSearch:
    """IOC Search Class."""

    _service_list = list()
    _ioc_list = list()
    _service_2_ioc_dict = dict()
    _service_2_prefix_dict = dict()
    _ioc_2_service_dict = dict()
    _ioc_2_prefix_dict = dict()

    _lock = _Lock()

    @staticmethod
    def get_services(pattern='.*'):
        """Return a sorted and filtered list of services."""
        IOCSearch._reload_service_2_ioc_dict()
        pattern = _re.compile(pattern)
        auxlist = list()
        for serv in IOCSearch._service_list:
            if pattern.match(serv):
                auxlist.append(serv)
        return auxlist

    @staticmethod
    def get_iocs(pattern='.*'):
        """Return a sorted and filtered list of IOCs."""
        IOCSearch._reload_service_2_ioc_dict()
        pattern = _re.compile(pattern)
        auxlist = list()
        for ioc in IOCSearch._ioc_list:
            if pattern.match(ioc):
                auxlist.append(ioc)
        return auxlist

    @staticmethod
    def conv_service_2_ioc(service):
        """Return IOCs associated with a service."""
        IOCSearch._reload_service_2_ioc_dict()
        return IOCSearch._service_2_ioc_dict[service]

    @staticmethod
    def conv_ioc_2_service(ioc):
        """Return service associated with an IOC."""
        IOCSearch._reload_service_2_ioc_dict()
        return IOCSearch._ioc_2_service_dict[ioc]

    @staticmethod
    def conv_ioc_2_prefix(ioc):
        """Return PV prefixes associated with a ioc."""
        IOCSearch._reload_service_2_ioc_dict()
        return IOCSearch._ioc_2_prefix_dict[ioc]

    @staticmethod
    def conv_service_2_prefix(service):
        """Return PV prefixes associated with a service."""
        IOCSearch._reload_service_2_ioc_dict()
        iocs = IOCSearch.conv_service_2_ioc(service)
        prefixes = list()
        for ioc in iocs:
            pref = IOCSearch._ioc_2_prefix_dict[ioc]
            prefixes.extend(pref)
        return prefixes

    @staticmethod
    def conv_prefix_2_ioc(prefix_pattern):
        """Return IOCs that match a prefix pattern."""
        IOCSearch._reload_service_2_ioc_dict()
        pattern = _re.compile(prefix_pattern)
        iocs = set()
        for ioc in IOCSearch._ioc_list:
            prefixes = IOCSearch._ioc_2_prefix_dict[ioc]
            for pref in prefixes:
                if pattern.match(pref):
                    iocs.add(ioc)
        return iocs

    @staticmethod
    def conv_prefix_2_service(prefix_pattern):
        """Return services that match a prefix pattern."""
        IOCSearch._reload_service_2_ioc_dict()
        iocs = IOCSearch.conv_prefix_2_ioc(prefix_pattern)
        services = set()
        for ioc in iocs:
            serv = IOCSearch.conv_ioc_2_service(ioc)
            services.add(serv)
        return services

    @staticmethod
    def _reload_service_2_ioc_dict():
        """Load service to IOC data to a dict."""
        with IOCSearch._lock:
            if IOCSearch._service_2_ioc_dict:
                return
            if not _web.server_online():
                raise Exception(
                    'could not read service to IOC table from web server')
            text = _web.doc_services_read()
            data = _yaml.load(text)
            service_2_ioc_dict = dict()
            ioc_2_prefix_dict = dict()
            for service, ioc2pref in data.items():
                service_2_ioc_dict[service] = [ioc for ioc in ioc2pref]
                ioc_2_prefix_dict.update(ioc2pref)
            IOCSearch._service_2_ioc_dict = service_2_ioc_dict
            IOCSearch._ioc_2_prefix_dict = ioc_2_prefix_dict
            IOCSearch._service_list = sorted(list(service_2_ioc_dict.keys()))
            IOCSearch._ioc_list = sorted(list(ioc_2_prefix_dict.keys()))

            ioc_2_service_dict = dict()
            for serv, iocs in IOCSearch._service_2_ioc_dict.items():
                ioc_2_service_dict.update({i: serv for i in iocs})
            IOCSearch._ioc_2_service_dict = ioc_2_service_dict
