#!/usr/bin/env python3
"""IOC Module."""
import sys as _sys
import logging as _log
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import signal as _signal
import main as _main
from siriuspy.util import get_last_commit_hash as _get_version
from siriuspy.envars import vaca_prefix as PREFIX

__version__ = _get_version()
INTERVAL = 0.1
stop_event = False  # _multiprocessing.Event()
PREFIX += 'SI-Glob:AP-Orbit:'
DB_FILENAME = 'pvs/si-ap-orbit-pvs.txt'


def _stop_now(signum, frame):
    _log.info('SIGNAL received')
    global stop_event
    stop_event = True


def _print_pvs_in_file(db):
    with open(DB_FILENAME, 'w') as f:
        for key in sorted(db.keys()):
            f.write(PREFIX+'{0:20s}\n'.format(key))
    _log.info(DB_FILENAME+' file generated with {0:d} pvs.'.format(len(db)))


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


def run(add_noise=False, debug=False):
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
    app.add_noise = add_noise
    _log.info('Generating database file.')
    db = app.get_database()
    db.update({PREFIX+'Version-Cte': {'type': 'string', 'value': __version__}})
    _print_pvs_in_file(db)

    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _log.info('Setting Server Database.')
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
