#!/usr/local/bin/python-sirius
import logging
import sys

from pcaspy import SimpleServer

from .driver import DiffPVs  # PCaspy Driver
from siriuspy.search import PSSearch
from siriuspy.envars import vaca_prefix
from siriuspy.util import configure_log_file, print_ioc_banner


def run(section='', sub_section='', device='', debug=False):
    """Run IOC."""
    configure_log_file(debug=debug)

    logging.info("Loding power supplies")
    logging.info("{:12s}: {}".format('\tSection', section or 'None'))
    logging.info("{:12s}: {}".format('\tSub Section', sub_section or 'None'))
    logging.info("{:12s}: {}".format('\tDevice', device or 'None'))

    server = SimpleServer()
    device_filter = dict()
    if section:
        device_filter['sec'] = section
    if sub_section:
        device_filter['sub'] = sub_section
    if device:
        device_filter['dev'] = device
    devices = PSSearch.get_psnames(device_filter)

    if not devices:
        logging.warning('No devices found. Aborting.')
        sys.exit(0)

    for device in devices:
        logging.debug('{:32s}'.format(device))

    prefix = vaca_prefix
    pvdb = {device + ':Diff-Mon': {'value': 0} for device in devices}

    logging.info("Creating server with %d devices and '%s' prefix",
                 len(devices), prefix)
    server.createPV(prefix, pvdb)
    logging.info('Creating driver')
    try:
        driver = DiffPVs(devices)
    except Exception:
        logging.error('Failed to create driver. Aborting', exc_info=True)
        sys.exit(1)

    print_ioc_banner(
        'AS PS Diagnostic', pvdb,
        'IOC that provides current sp/mon diagnostics for the power supplies.',
        '0.1', prefix)

    driver.scanning = True
    while True:
        server.process(0.1)

    driver.scanning = False
    driver.quit = True
    sys.exit(0)
