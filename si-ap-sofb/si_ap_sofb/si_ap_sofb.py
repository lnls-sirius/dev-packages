#!/usr/bin/env python3
"""IOC Module."""

import os as _os
import sys as _sys
import logging as _log
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import signal as _signal
from si_ap_sofb import main as _main
from si_ap_sofb.definitions import print_pvs_in_file
from si_ap_sofb.definitions import __version__, PREFIX, INTERVAL

stop_event = False


def _stop_now(signum, frame):
    _log.info('SIGNAL received')
    global stop_event
    stop_event = True


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app.driver = self

    def read(self, reason):
        _log.debug("Reading {0:s}.".format(reason))
        return super().read(reason)

    def write(self, reason, value):
        app_ret = self.app.write(reason, value)
        if app_ret:
            self.setParam(reason, value)
        else:
            self.setParam(reason, self.getParam(reason))
        self.updatePVs()
        return True


def run(debug=False):
    """Start the IOC."""
    level = _log.DEBUG if debug else _log.INFO
    fmt = ('%(levelname)7s | %(asctime)s | ' +
           '%(module)15s.%(funcName)20s[%(lineno)4d] ::: %(message)s')
    _log.basicConfig(format=fmt, datefmt='%F %T', level=level,
                     stream=_sys.stdout)
    #  filename=LOG_FILENAME, filemode='w')
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # Creates App object
    _log.info('Creating App.')
    app = _main.App()
    _log.info('Generating database file.')
    db = app.get_database()
    db.update({'Version-Cte': {'type': 'string', 'value': __version__}})
    print_pvs_in_file(db)

    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _log.info('Setting Server Database.')
    _attribute_access_security_group(server, db)
    server.createPV(PREFIX, db)
    _log.info('Creating Driver.')
    pcas_driver = _PCASDriver(app)

    # Connects to low level PVs
    _log.info('Openning connections with Low Level IOCs.')
    app.connect()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    _log.info('Starting Server Thread.')
    server_thread.start()

    # main loop
    # while not stop_event.is_set():
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')


if __name__ == '__main__':
    run()
