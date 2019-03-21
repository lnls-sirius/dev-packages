#!/usr/local/bin/python-sirius
"""AS PS Diagnostic."""

import logging as _log
import sys as _sys
import pcaspy as _pcaspy

from .driver import PSDiagDriver as _PSDiagDriver

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.util import configure_log_file as _config_log_file
from siriuspy.util import print_ioc_banner as _print_ioc_banner


def run(section='', sub_section='', device='', debug=False):
    """Run IOC."""
    _config_log_file(debug=debug)

    _log.info("Loding power supplies")
    _log.info("{:12s}: {}".format('\tSection', section or 'None'))
    _log.info("{:12s}: {}".format('\tSub Section', sub_section or 'None'))
    _log.info("{:12s}: {}".format('\tDevice', device or 'None'))

    server = _pcaspy.SimpleServer()
    device_filter = dict()
    if section:
        device_filter['sec'] = section
    if sub_section:
        device_filter['sub'] = sub_section
    if device:
        device_filter['dev'] = device
    device_filter['dis'] = 'PS'
    devices = _PSSearch.get_psnames(device_filter)

    if not devices:
        _log.warning('No devices found. Aborting.')
        _sys.exit(0)

    for device in devices:
        _log.debug('{:32s}'.format(device))

    prefix = _vaca_prefix
    pvdb = {
        device + ':Diag-Mon': {
            'value': 0,
            'hilim': 1,
            'hihi': 1,
            'high': 1,
            'lolim': -1,
            'lolo': -1,
            'low': -1,
        } for device in devices
    }

    _log.info("Creating server with %d devices and '%s' prefix",
              len(devices), prefix)
    server.createPV(prefix, pvdb)
    _log.info('Creating driver')
    try:
        driver = _PSDiagDriver(devices)
    except Exception:
        _log.error('Failed to create driver. Aborting', exc_info=True)
        _sys.exit(1)

    _print_ioc_banner(
        'AS PS Diagnostic', pvdb,
        'IOC that provides current sp/mon diagnostics for the power supplies.',
        '0.1', prefix)

    driver.scanning = True
    while True:
        server.process(0.1)

    driver.scanning = False
    driver.quit = True
    _sys.exit(0)
